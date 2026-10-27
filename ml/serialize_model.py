from __future__ import annotations

import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sklearn
import xgboost
import skops
import skops.io as sio


ROOT = Path(__file__).resolve().parents[1]

SOURCE_MODEL = ROOT / "ml" / "models" / "xgboost_tuned_cv_v1.joblib"
EVALUATION_REPORT = (
    ROOT / "ml" / "reports" / "formal_holdout_evaluation_v1.json"
)
TRAINING_REPORT = (
    ROOT / "ml" / "reports" / "candidate_model_training_report.json"
)

OUTPUT_DIR = ROOT / "ml" / "reports" / "model_registry"
MODEL_DIR = ROOT / "ml" / "models"

MODEL_ID = "churnguard-xgboost-v1"
BUSINESS_THRESHOLD = 0.45


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def load_json(path: Path) -> dict:
    if not path.is_file():
        raise FileNotFoundError(f"Required report not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def main() -> None:
    print("=" * 72)
    print("ChurnGuard — Model Serialization and Versioning")
    print("=" * 72)

    if not SOURCE_MODEL.is_file():
        raise FileNotFoundError(
            f"Trained model not found: {SOURCE_MODEL}"
        )

    evaluation = load_json(EVALUATION_REPORT)
    training = load_json(TRAINING_REPORT)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    print("\n[1/6] Loading existing model...")
    model = joblib.load(SOURCE_MODEL)

    if not hasattr(model, "named_steps"):
        raise TypeError("Expected a fitted sklearn Pipeline.")

    steps = list(model.named_steps)
    if steps != ["preprocess", "model"]:
        raise ValueError(
            f"Unexpected pipeline steps: {steps}"
        )

    print("Pipeline steps:", steps)
    print("Source SHA-256:", sha256_file(SOURCE_MODEL))

    print("\n[2/6] Checking evaluation reports...")
    evaluation_text = json.dumps(evaluation).lower()
    training_text = json.dumps(training).lower()

    if "xgboost" not in evaluation_text:
        raise ValueError(
            "Evaluation report does not identify XGBoost."
        )

    if "xgboost" not in training_text:
        raise ValueError(
            "Training report does not identify XGBoost."
        )

    print("Training and evaluation reports found.")
    print(
        "Note: report identity is checked; metric values "
        "must be reviewed against the original reports."
    )

    print("\n[3/6] Writing versioned joblib artifact...")
    joblib_path = MODEL_DIR / f"{MODEL_ID}.joblib"
    joblib.dump(model, joblib_path)

    print("\n[4/6] Writing skops artifact...")
    skops_path = MODEL_DIR / f"{MODEL_ID}.skops"
    sio.dump(model, skops_path)

    print("\n[5/6] Verifying serialization round trips...")
    original_steps = list(model.named_steps)

    restored_joblib = joblib.load(joblib_path)
    restored_skops = sio.load(
        skops_path,
        trusted=sio.get_untrusted_types(file=skops_path),
    )

    for label, restored in (
        ("joblib", restored_joblib),
        ("skops", restored_skops),
    ):
        if list(restored.named_steps) != original_steps:
            raise AssertionError(
                f"{label} round-trip changed pipeline steps."
            )

    # Compare probabilities using a synthetic row with the
    # exact feature names and categorical/numeric structure
    # expected by the fitted preprocessing pipeline.
    preprocessor = model.named_steps["preprocess"]
    transformers = preprocessor.transformers_

    numeric_columns = []
    categorical_columns = []

    for name, _, columns in transformers:
        if name == "numeric":
            numeric_columns.extend(columns)
        elif name == "categorical":
            categorical_columns.extend(columns)

    row = {}

    for column in numeric_columns:
        row[column] = 1.0

    for column in categorical_columns:
        row[column] = "No"

    sample = pd.DataFrame([row])

    expected = model.predict_proba(sample)
    joblib_actual = restored_joblib.predict_proba(sample)
    skops_actual = restored_skops.predict_proba(sample)

    np.testing.assert_allclose(
        expected, joblib_actual, rtol=1e-6, atol=1e-7
    )
    np.testing.assert_allclose(
        expected, skops_actual, rtol=1e-6, atol=1e-7
    )

    print("joblib round-trip: PASS")
    print("skops round-trip: PASS")
    print("Prediction parity: PASS")

    print("\n[6/6] Writing model manifest...")
    manifest = {
        "model_id": MODEL_ID,
        "model_family": "XGBoost",
        "source_artifact": str(SOURCE_MODEL.relative_to(ROOT)),
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "business_threshold": BUSINESS_THRESHOLD,
        "threshold_note": (
            "Applied by the decision layer, not embedded "
            "in the probability estimator."
        ),
        "pipeline_steps": original_steps,
        "artifacts": {
            "joblib": {
                "path": str(joblib_path.relative_to(ROOT)),
                "sha256": sha256_file(joblib_path),
                "bytes": joblib_path.stat().st_size,
            },
            "skops": {
                "path": str(skops_path.relative_to(ROOT)),
                "sha256": sha256_file(skops_path),
                "bytes": skops_path.stat().st_size,
            },
        },
        "source_artifact_sha256": sha256_file(SOURCE_MODEL),
        "reports": {
            "training": str(TRAINING_REPORT.relative_to(ROOT)),
            "evaluation": str(EVALUATION_REPORT.relative_to(ROOT)),
        },
        "runtime": {
            "python": sys.version,
            "platform": platform.platform(),
            "scikit_learn": sklearn.__version__,
            "xgboost": xgboost.__version__,
            "joblib": joblib.__version__,
            "skops": skops.__version__,
        },
        "verification": {
            "pipeline_steps_match": True,
            "joblib_round_trip": True,
            "skops_round_trip": True,
            "prediction_parity": True,
        },
        "limitations": [
            "This manifest records artifact identity and serialization checks.",
            "It does not establish independent reproducibility of training.",
            "It does not register the model in MLflow.",
        ],
    }

    manifest_path = OUTPUT_DIR / f"{MODEL_ID}_manifest.json"

    with manifest_path.open("w", encoding="utf-8") as file:
        json.dump(manifest, file, indent=2, ensure_ascii=False)

    print("\n" + "=" * 72)
    print("MODEL SERIALIZATION STAGE PASSED")
    print("=" * 72)
    print(f"Joblib:   {joblib_path}")
    print(f"Skops:    {skops_path}")
    print(f"Manifest: {manifest_path}")
    print(f"Threshold: {BUSINESS_THRESHOLD:.2f}")
    print("\nNo model training was performed.")


if __name__ == "__main__":
    main()
