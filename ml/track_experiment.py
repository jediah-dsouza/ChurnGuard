
from __future__ import annotations

import json
from pathlib import Path

import mlflow
from mlflow import MlflowClient


ROOT = Path(__file__).resolve().parents[1]

REGISTRY_DIR = ROOT / "ml" / "reports" / "model_registry"
MANIFEST_PATH = (
    REGISTRY_DIR / "churnguard-xgboost-v1_manifest.json"
)
EVALUATION_PATH = (
    ROOT / "ml" / "reports" / "formal_holdout_evaluation_v1.json"
)
TRAINING_PATH = (
    ROOT / "ml" / "reports" / "candidate_model_training_report.json"
)
MODEL_PATH = (
    ROOT / "ml" / "models" / "churnguard-xgboost-v1.joblib"
)
SKOPS_PATH = (
    ROOT / "ml" / "models" / "churnguard-xgboost-v1.skops"
)

TRACKING_DIR = REGISTRY_DIR / "mlruns"
EXPERIMENT_NAME = "ChurnGuard"
RUN_NAME = "churnguard-xgboost-v1-holdout-evaluation"


def read_json(path: Path) -> dict:
    if not path.is_file():
        raise FileNotFoundError(f"Required file not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def main() -> None:
    print("=" * 72)
    print("ChurnGuard — MLflow Experiment Tracking")
    print("=" * 72)

    manifest = read_json(MANIFEST_PATH)
    evaluation = read_json(EVALUATION_PATH)
    training = read_json(TRAINING_PATH)

    for path in (MODEL_PATH, SKOPS_PATH):
        if not path.is_file():
            raise FileNotFoundError(f"Model artifact not found: {path}")

    if manifest.get("model_id") != "churnguard-xgboost-v1":
        raise ValueError("Unexpected model ID in manifest.")

    if manifest.get("verification", {}).get("prediction_parity") is not True:
        raise ValueError("Manifest does not confirm prediction parity.")

    TRACKING_DIR.mkdir(parents=True, exist_ok=True)

    # Use a local SQLite database for metadata and a separate
    # local directory for run artifacts.
    database_path = (REGISTRY_DIR / "mlflow.db").resolve()
    artifact_path = TRACKING_DIR.resolve()

    tracking_uri = f"sqlite:///{database_path.as_posix()}"
    artifact_uri = artifact_path.as_uri()

    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_registry_uri(tracking_uri)
    mlflow.set_experiment(EXPERIMENT_NAME)

    client = MlflowClient()
    experiment = client.get_experiment_by_name(EXPERIMENT_NAME)

    if experiment is None:
        raise RuntimeError("MLflow experiment was not created.")

    print(f"Tracking URI: {tracking_uri}")
    print(f"Experiment:   {EXPERIMENT_NAME}")
    print(f"Artifact dir: {artifact_uri}")

    with mlflow.start_run(
        experiment_id=experiment.experiment_id,
        run_name=RUN_NAME,
    ) as run:
        mlflow.set_tags(
            {
                "project": "ChurnGuard",
                "model_id": manifest["model_id"],
                "model_family": manifest["model_family"],
                "stage": "formal_holdout_evaluation",
                "model_training_performed": "false",
                "serialization_verified": "true",
            }
        )

        mlflow.log_params(
            {
                "model_id": manifest["model_id"],
                "model_family": manifest["model_family"],
                "business_threshold": manifest["business_threshold"],
                "pipeline_steps": ",".join(manifest["pipeline_steps"]),
                "python_version": manifest["runtime"]["python"].split()[0],
                "scikit_learn_version": manifest["runtime"]["scikit_learn"],
                "xgboost_version": manifest["runtime"]["xgboost"],
                "skops_version": manifest["runtime"]["skops"],
            }
        )

        # Keep the complete source reports available with the run.
        mlflow.log_artifact(str(MANIFEST_PATH), artifact_path="metadata")
        mlflow.log_artifact(str(EVALUATION_PATH), artifact_path="reports")
        mlflow.log_artifact(str(TRAINING_PATH), artifact_path="reports")

        # Preserve the exact serialized model files as run artifacts.
        mlflow.log_artifact(str(MODEL_PATH), artifact_path="model_artifacts")
        mlflow.log_artifact(str(SKOPS_PATH), artifact_path="model_artifacts")

        # Record the already-established evaluation results.
        # These values are not recomputed or changed by this script.
        holdout_metrics = {
            "holdout_accuracy": 0.7566,
            "holdout_precision_default": 0.5283,
            "holdout_recall_default": 0.7727,
            "holdout_f1_default": 0.6276,
            "holdout_roc_auc": 0.8485,
            "holdout_pr_auc": 0.6617,
            "holdout_recall_threshold_045": 0.8075,
            "holdout_precision_threshold_045": 0.5127,
            "holdout_f1_threshold_045": 0.6272,
            "holdout_predicted_positive_rate_threshold_045": 0.4180,
        }

        mlflow.log_metrics(holdout_metrics)

        # Verify that the run can be retrieved after logging.
        run_id = run.info.run_id

    stored_run = client.get_run(run_id)
    stored_metrics = stored_run.data.metrics

    if "holdout_roc_auc" not in stored_metrics:
        raise RuntimeError("MLflow metric verification failed.")

    if abs(stored_metrics["holdout_roc_auc"] - 0.8485) > 1e-9:
        raise RuntimeError("Stored ROC-AUC differs from expected value.")

    print("\n" + "=" * 72)
    print("MLFLOW TRACKING STAGE PASSED")
    print("=" * 72)
    print(f"Experiment ID: {experiment.experiment_id}")
    print(f"Run ID:        {run_id}")
    print(f"Run name:      {stored_run.data.tags.get('mlflow.runName')}")
    print(f"ROC-AUC:       {stored_metrics['holdout_roc_auc']:.4f}")
    print(f"PR-AUC:        {stored_metrics['holdout_pr_auc']:.4f}")
    print(f"Threshold:     {manifest['business_threshold']:.2f}")
    print(f"Tracking DB:   {database_path}")
    print("\nModel training was not performed.")
    print("The model has not yet been registered in the MLflow Model Registry.")


if __name__ == "__main__":
    main()
