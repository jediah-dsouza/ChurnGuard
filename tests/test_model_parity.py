import os
from pathlib import Path

import joblib
import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
MODEL_NAME = "ChurnGuard-XGBoost"
MODEL_VERSION = "1"
THRESHOLD = 0.45


def test_local_and_registered_models_have_prediction_parity():
    registry_dir = ROOT / "ml" / "reports" / "model_registry"
    db_path = (registry_dir / "mlflow.db").resolve()
    tracking_uri = f"sqlite:///{db_path.as_posix()}"

    assert db_path.exists(), f"MLflow database not found: {db_path}"

    mlflow.set_tracking_uri(tracking_uri)

    local_path = ROOT / "ml" / "models" / "churnguard-xgboost-v1.joblib"
    data_path = ROOT / "ml" / "data" / "WA_Fn-UseC_-Telco-Customer-Churn.csv"

    assert local_path.exists(), f"Local model not found: {local_path}"
    assert data_path.exists(), f"Dataset not found: {data_path}"

    local_model = joblib.load(local_path)
    registered_model = mlflow.sklearn.load_model(
        f"models:/{MODEL_NAME}/{MODEL_VERSION}"
    )

    df = pd.read_csv(data_path)
    feature_names = list(local_model.feature_names_in_)
    assert list(registered_model.feature_names_in_) == feature_names

    # Deterministic sample spanning the dataset; labels are not used.
    indices = np.linspace(0, len(df) - 1, num=32, dtype=int)
    X = df.loc[:, feature_names].iloc[indices].copy()

    def churn_probability(model, frame):
        classes = list(model.classes_)
        assert 1 in classes, f"Churn class 1 missing from {classes}"
        return model.predict_proba(frame)[:, classes.index(1)]

    local_probs = churn_probability(local_model, X)
    registered_probs = churn_probability(registered_model, X)

    assert np.isfinite(local_probs).all()
    assert np.isfinite(registered_probs).all()
    np.testing.assert_allclose(
        local_probs,
        registered_probs,
        atol=1e-6,
        rtol=0,
        err_msg="Local and registered MLflow probabilities differ",
    )

    np.testing.assert_array_equal(
        local_probs >= THRESHOLD,
        registered_probs >= THRESHOLD,
        err_msg="Local and registered model decisions differ at threshold 0.45",
    )
