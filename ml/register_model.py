from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import mlflow
import pandas as pd
from mlflow import MlflowClient
from mlflow.models import infer_signature


# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]

REGISTRY_DIR = ROOT / "ml" / "reports" / "model_registry"
MANIFEST_PATH = REGISTRY_DIR / "churnguard-xgboost-v1_manifest.json"
MODEL_PATH = ROOT / "ml" / "models" / "churnguard-xgboost-v1.joblib"

EXPERIMENT_NAME = "ChurnGuard"
MODEL_NAME = "ChurnGuard-XGBoost"
EXPECTED_MODEL_ID = "churnguard-xgboost-v1"
EXPECTED_ROC_AUC = 0.8485

DATABASE_PATH = (REGISTRY_DIR / "mlflow.db").resolve()
TRACKING_URI = f"sqlite:///{DATABASE_PATH.as_posix()}"

# These types were identified by the earlier serialization checks.
SKOPS_TRUSTED_TYPES = [
    "numpy.dtype",
    "xgboost.core.Booster",
    "xgboost.sklearn.XGBClassifier",
]


# ---------------------------------------------------------------------
# Manifest validation
# ---------------------------------------------------------------------

def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError(f"Expected a JSON object in {path}")

    return data


def validate_manifest(manifest: dict[str, Any]) -> None:
    if manifest.get("model_id") != EXPECTED_MODEL_ID:
        raise ValueError(
            "Manifest model_id does not match the expected model ID. "
            f"Expected {EXPECTED_MODEL_ID!r}, "
            f"got {manifest.get('model_id')!r}."
        )

    verification = manifest.get("verification", {})

    if not isinstance(verification, dict):
        raise ValueError("Manifest 'verification' must be a JSON object.")

    required_checks = (
        "pipeline_steps_match",
        "joblib_round_trip",
        "skops_round_trip",
        "prediction_parity",
    )

    failed_checks = [
        check
        for check in required_checks
        if verification.get(check) is not True
    ]

    if failed_checks:
        raise ValueError(
            "Model manifest verification is incomplete or unsuccessful: "
            + ", ".join(failed_checks)
        )


# ---------------------------------------------------------------------
# Find the original evaluation run
# ---------------------------------------------------------------------

def find_evaluation_run(
    client: MlflowClient,
    experiment_id: str,
):
    """
    Find the recorded formal holdout evaluation.

    This deliberately does not require status == FINISHED because the
    existing evaluation run contains valid recorded metrics but was
    subsequently marked FAILED during the earlier registration attempt.
    The original run is read only; it is not reopened or modified.
    """
    runs = client.search_runs(
        experiment_ids=[experiment_id],
        filter_string="tags.model_id = 'churnguard-xgboost-v1'",
        order_by=["attributes.start_time DESC"],
        max_results=100,
    )

    valid_runs = []

    for run in runs:
        tags = run.data.tags
        metrics = run.data.metrics

        if tags.get("serialization_verified") != "true":
            continue

        if tags.get("stage") != "formal_holdout_evaluation":
            continue

        if "holdout_roc_auc" not in metrics:
            continue

        if "holdout_pr_auc" not in metrics:
            continue

        valid_runs.append(run)

    if not valid_runs:
        raise RuntimeError(
            "No matching holdout evaluation run was found. "
            "Expected model_id='churnguard-xgboost-v1', "
            "serialization_verified='true', stage="
            "'formal_holdout_evaluation', and recorded ROC-AUC/PR-AUC."
        )

    # Prefer a run with the expected recorded ROC-AUC.
    expected_runs = [
        run
        for run in valid_runs
        if abs(
            run.data.metrics["holdout_roc_auc"] - EXPECTED_ROC_AUC
        ) < 1e-6
    ]

    if not expected_runs:
        observed = [
            run.data.metrics.get("holdout_roc_auc")
            for run in valid_runs
        ]
        raise RuntimeError(
            f"No matching evaluation run has the expected ROC-AUC "
            f"{EXPECTED_ROC_AUC}. Recorded values: {observed}"
        )

    return expected_runs[0]


# ---------------------------------------------------------------------
# Build a sample matching the pipeline's original input columns
# ---------------------------------------------------------------------

def build_input_example(pipeline):
    feature_names = getattr(pipeline, "feature_names_in_", None)

    if feature_names is None:
        raise RuntimeError(
            "The saved pipeline does not expose feature_names_in_. "
            "Cannot safely construct an input example automatically."
        )

    numeric_defaults = {
        "tenure": 12,
        "MonthlyCharges": 70.0,
        "TotalCharges": 840.0,
        "SeniorCitizen": 0,
    }

    sample_values = {}

    for column in feature_names:
        if column in numeric_defaults:
            sample_values[column] = numeric_defaults[column]
        elif column == "customerID":
            sample_values[column] = "0001-TEST"
        elif column == "gender":
            sample_values[column] = "Female"
        else:
            sample_values[column] = "No"

    sample = pd.DataFrame(
        [sample_values],
        columns=list(feature_names),
    )

    # Confirm the pipeline can process the example before logging it.
    probabilities = pipeline.predict_proba(sample)

    if probabilities.ndim != 2 or probabilities.shape[0] != 1:
        raise RuntimeError(
            "The pipeline returned an unexpected predict_proba shape: "
            f"{probabilities.shape}"
        )

    signature = infer_signature(sample, probabilities)

    return sample, signature


# ---------------------------------------------------------------------
# Idempotency check
# ---------------------------------------------------------------------

def find_existing_registration(
    client: MlflowClient,
    evaluation_run_id: str,
):
    """
    Avoid creating another model version if a prior attempt already
    registered this model from a registration run linked to this
    evaluation run.
    """
    try:
        versions = client.search_model_versions(
            f"name='{MODEL_NAME}'"
        )
    except Exception:
        # The registered model may not exist yet.
        return None

    for version in versions:
        registration_run_id = getattr(version, "run_id", None)

        if not registration_run_id:
            continue

        try:
            registration_run = client.get_run(registration_run_id)
        except Exception:
            continue

        source_evaluation_id = registration_run.data.tags.get(
            "source_evaluation_run_id"
        )

        if source_evaluation_id == evaluation_run_id:
            return version

    return None


# ---------------------------------------------------------------------
# Main registration workflow
# ---------------------------------------------------------------------

def main() -> None:
    if not MANIFEST_PATH.is_file():
        raise FileNotFoundError(
            f"Model manifest was not found: {MANIFEST_PATH}"
        )

    if not MODEL_PATH.is_file():
        raise FileNotFoundError(
            f"Serialized model was not found: {MODEL_PATH}"
        )

    REGISTRY_DIR.mkdir(parents=True, exist_ok=True)

    manifest = read_json(MANIFEST_PATH)
    validate_manifest(manifest)

    # Use the same SQLite database for tracking and model registry.
    mlflow.set_tracking_uri(TRACKING_URI)
    mlflow.set_registry_uri(TRACKING_URI)

    client = MlflowClient(
        tracking_uri=TRACKING_URI,
        registry_uri=TRACKING_URI,
    )

    experiment = client.get_experiment_by_name(EXPERIMENT_NAME)

    if experiment is None:
        raise RuntimeError(
            f"MLflow experiment {EXPERIMENT_NAME!r} was not found "
            f"in {DATABASE_PATH}. Refusing to create a new experiment "
            "because the existing evaluation history must be preserved."
        )

    evaluation_run = find_evaluation_run(
        client,
        experiment.experiment_id,
    )

    evaluation_metrics = evaluation_run.data.metrics

    print("Evaluation run found:")
    print(f"  Run ID:  {evaluation_run.info.run_id}")
    print(f"  Status:  {evaluation_run.info.status}")
    print(
        "  ROC-AUC: "
        f"{evaluation_metrics['holdout_roc_auc']:.4f}"
    )
    print(
        "  PR-AUC:  "
        f"{evaluation_metrics['holdout_pr_auc']:.4f}"
    )

    # Check for a previously completed registration before creating
    # another model version.
    existing_version = find_existing_registration(
        client,
        evaluation_run.info.run_id,
    )

    if existing_version is not None:
        print("\nA model version linked to this evaluation already exists.")
        print(f"  Registered model: {MODEL_NAME}")
        print(f"  Version:          {existing_version.version}")
        print(f"  Status:           {existing_version.status}")
        print("No additional model version was created.")
        return

    # Load the exact, already-serialized pipeline. Do not retrain.
    pipeline = joblib.load(MODEL_PATH)

    sample, signature = build_input_example(pipeline)

    # Create a NEW run for registration. Never reopen the original
    # holdout evaluation run, which may be marked FAILED.
    with mlflow.start_run(
        experiment_id=experiment.experiment_id,
        run_name="churnguard-xgboost-v1-model-registration",
    ) as registration_run:
        mlflow.set_tags(
            {
                "project": "ChurnGuard",
                "model_id": EXPECTED_MODEL_ID,
                "model_family": "XGBoost",
                "stage": "model_registration",
                "source_evaluation_run_id": evaluation_run.info.run_id,
                "serialization_verified": "true",
                "model_training_performed": "false",
            }
        )

        # Copy the source evaluation metrics into the new registration
        # run for convenient traceability. These are not new evaluations.
        mlflow.log_metrics(
            {
                "source_holdout_roc_auc": evaluation_metrics[
                    "holdout_roc_auc"
                ],
                "source_holdout_pr_auc": evaluation_metrics[
                    "holdout_pr_auc"
                ],
            }
        )

        model_info = mlflow.sklearn.log_model(
            sk_model=pipeline,
            name="model",
            signature=signature,
            input_example=sample,
            registered_model_name=MODEL_NAME,
            skops_trusted_types=SKOPS_TRUSTED_TYPES,
        )

        print("\nModel logging completed.")
        print(f"  Registered model: {MODEL_NAME}")
        print(f"  Model URI:        {model_info.model_uri}")
        print(f"  Registration run: {registration_run.info.run_id}")
        print(f"  Evaluation run:   {evaluation_run.info.run_id}")

    # Verify that a registered version references the new registration
    # run. This check happens after the registration run has ended.
    registered_versions = client.search_model_versions(
        f"name='{MODEL_NAME}'"
    )

    matching_versions = [
        version
        for version in registered_versions
        if getattr(version, "run_id", None) == registration_run.info.run_id
    ]

    if not matching_versions:
        raise RuntimeError(
            "MLflow logging returned, but no registered model version "
            "was found for the registration run. Check the MLflow UI "
            "and the registration run's artifacts before retrying."
        )

    registered_version = matching_versions[0]

    print("\nRegistration verified.")
    print(f"  Registered model: {MODEL_NAME}")
    print(f"  Version:          {registered_version.version}")
    print(f"  Version status:   {registered_version.status}")
    print(f"  Source run:       {registered_version.run_id}")
    print(f"  Evaluation AUC:   {EXPECTED_ROC_AUC:.4f}")
    print("\nNo model training or holdout re-evaluation was performed.")


if __name__ == "__main__":
    main()
