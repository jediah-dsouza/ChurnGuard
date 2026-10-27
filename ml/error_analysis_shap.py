from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
import shap
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split


# ============================================================
# CONFIGURATION
# ============================================================

# Project root:
# C:\Users\Jediah\Downloads\ChurnGuard-Frontend\ChurnGuard
ROOT = Path(__file__).resolve().parents[1]

# Actual ML directories.
DATA_PATH = (
    ROOT
    / "ml"
    / "data"
    / "WA_Fn-UseC_-Telco-Customer-Churn.csv"
)

MODEL_PATH = (
    ROOT
    / "ml"
    / "models"
    / "xgboost_tuned_cv_v1.joblib"
)

REPORT_DIR = ROOT / "ml" / "reports"

ERROR_DIR = REPORT_DIR / "error_analysis"
SHAP_DIR = REPORT_DIR / "shap"

TARGET_COLUMN = "Churn"

# Locked split configuration.
RANDOM_STATE = 42
HOLDOUT_SIZE = 0.20

# Locked business threshold from formal holdout evaluation.
BUSINESS_THRESHOLD = 0.45

# Required local SHAP explanations.
LOCAL_EXPLANATION_COUNT = 3


# ============================================================
# GENERAL HELPERS
# ============================================================

def ensure_directories() -> None:
    """Create output directories."""
    ERROR_DIR.mkdir(parents=True, exist_ok=True)
    SHAP_DIR.mkdir(parents=True, exist_ok=True)


def json_default(value: Any) -> Any:
    """Convert NumPy/Pandas values into JSON-safe values."""

    if isinstance(value, np.integer):
        return int(value)

    if isinstance(value, np.floating):
        return float(value)

    if isinstance(value, np.bool_):
        return bool(value)

    if isinstance(value, np.ndarray):
        return value.tolist()

    if isinstance(value, pd.Timestamp):
        return value.isoformat()

    raise TypeError(
        f"Object of type {type(value).__name__} "
        "is not JSON serializable"
    )


def write_json(
    path: Path,
    payload: Any,
) -> None:
    """Write formatted JSON."""

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open(
        "w",
        encoding="utf-8",
    ) as handle:
        json.dump(
            payload,
            handle,
            indent=2,
            default=json_default,
        )


# ============================================================
# DATASET
# ============================================================

def load_raw_dataset() -> pd.DataFrame:
    """Load the clean Telco Customer Churn dataset."""

    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_PATH}"
        )

    df = pd.read_csv(DATA_PATH)

    if TARGET_COLUMN not in df.columns:
        raise ValueError(
            f"Target column '{TARGET_COLUMN}' "
            "is missing from the dataset."
        )

    return df


def prepare_modeling_frame(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.Series]:
    """
    Reconstruct the clean modeling frame.

    Rules:
    - customerID is excluded.
    - Churn is the target.
    - TotalCharges is converted to numeric.
    - Target-derived leakage columns are rejected.
    """

    data = df.copy()

    # Match finalized data-preparation behavior.
    data["TotalCharges"] = pd.to_numeric(
        data["TotalCharges"],
        errors="coerce",
    )

    # Explicit leakage protection.
    leakage_columns = {
        "churn_risk_score",
        "post_outcome_churn_flag",
    }

    detected_leakage = leakage_columns.intersection(
        data.columns
    )

    if detected_leakage:
        raise ValueError(
            "Potential target-derived leakage columns "
            f"detected: {sorted(detected_leakage)}"
        )

    # Convert target.
    y = data[TARGET_COLUMN].map(
        {
            "No": 0,
            "Yes": 1,
        }
    )

    if y.isna().any():
        raise ValueError(
            "Unexpected values found in the Churn target."
        )

    # Remove target and identifier.
    X = data.drop(
        columns=[
            TARGET_COLUMN,
            "customerID",
        ],
        errors="ignore",
    )

    return X, y.astype(int)


# ============================================================
# LOCKED HOLDOUT RECONSTRUCTION
# ============================================================

def reconstruct_locked_holdout(
    X: pd.DataFrame,
    y: pd.Series,
) -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.Series,
    pd.Series,
]:
    """
    Reconstruct the exact locked 80/20 stratified split.
    """

    (
        X_train,
        X_holdout,
        y_train,
        y_holdout,
    ) = train_test_split(
        X,
        y,
        test_size=HOLDOUT_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    return (
        X_train,
        X_holdout,
        y_train,
        y_holdout,
    )


# ============================================================
# MODEL
# ============================================================

def load_model():
    """Load the locked tuned XGBoost pipeline."""

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model not found: {MODEL_PATH}"
        )

    model = joblib.load(MODEL_PATH)

    if not hasattr(model, "named_steps"):
        raise TypeError(
            "Expected the saved model to be a "
            "scikit-learn Pipeline."
        )

    expected_steps = {
        "preprocess",
        "model",
    }

    actual_steps = set(
        model.named_steps.keys()
    )

    missing_steps = expected_steps - actual_steps

    if missing_steps:
        raise KeyError(
            "Saved pipeline is missing expected steps: "
            f"{sorted(missing_steps)}. "
            f"Available steps: {sorted(actual_steps)}"
        )

    return model


# ============================================================
# ERROR ANALYSIS
# ============================================================

def build_error_analysis(
    X_holdout: pd.DataFrame,
    y_holdout: pd.Series,
    probabilities: np.ndarray,
) -> tuple[
    pd.DataFrame,
    dict[str, Any],
]:
    """Generate row-level and segment-level error analysis."""

    predictions = (
        probabilities >= BUSINESS_THRESHOLD
    ).astype(int)

    (
        tn,
        fp,
        fn,
        tp,
    ) = confusion_matrix(
        y_holdout,
        predictions,
        labels=[0, 1],
    ).ravel()

    # --------------------------------------------------------
    # Row-level results
    # --------------------------------------------------------

    results = X_holdout.copy()

    actual_values = y_holdout.to_numpy()

    results["actual_churn"] = actual_values

    results["predicted_probability"] = probabilities

    results["predicted_churn"] = predictions

    results["prediction_error_type"] = np.select(
        [
            (actual_values == 0)
            & (predictions == 0),

            (actual_values == 0)
            & (predictions == 1),

            (actual_values == 1)
            & (predictions == 0),

            (actual_values == 1)
            & (predictions == 1),
        ],
        [
            "true_negative",
            "false_positive",
            "false_negative",
            "true_positive",
        ],
        default="unknown",
    )

    # --------------------------------------------------------
    # Segment analysis
    # --------------------------------------------------------

    candidate_segments = [
        "Contract",
        "tenure",
        "InternetService",
        "PaymentMethod",
        "SeniorCitizen",
        "Partner",
        "Dependents",
        "TechSupport",
        "OnlineSecurity",
    ]

    available_segments = [
        column
        for column in candidate_segments
        if column in results.columns
    ]

    segment_records: list[dict[str, Any]] = []

    for column in available_segments:

        grouped = results.groupby(
            column,
            dropna=False,
        )

        for segment_value, group in grouped:

            actual = group[
                "actual_churn"
            ].to_numpy()

            predicted = group[
                "predicted_churn"
            ].to_numpy()

            sample_count = len(group)

            actual_positive_count = int(
                (actual == 1).sum()
            )

            actual_negative_count = int(
                (actual == 0).sum()
            )

            false_negative_count = int(
                (
                    (actual == 1)
                    & (predicted == 0)
                ).sum()
            )

            false_positive_count = int(
                (
                    (actual == 0)
                    & (predicted == 1)
                ).sum()
            )

            false_negative_rate = (
                false_negative_count
                / actual_positive_count
                if actual_positive_count > 0
                else None
            )

            false_positive_rate = (
                false_positive_count
                / actual_negative_count
                if actual_negative_count > 0
                else None
            )

            if pd.isna(segment_value):
                display_value = "Missing"
            else:
                display_value = str(
                    segment_value
                )

            segment_records.append(
                {
                    "segment_column": column,
                    "segment_value": display_value,
                    "sample_count": sample_count,
                    "actual_churn_count": (
                        actual_positive_count
                    ),
                    "actual_non_churn_count": (
                        actual_negative_count
                    ),
                    "false_negative_count": (
                        false_negative_count
                    ),
                    "false_positive_count": (
                        false_positive_count
                    ),
                    "false_negative_rate": (
                        false_negative_rate
                    ),
                    "false_positive_rate": (
                        false_positive_rate
                    ),
                    "mean_predicted_probability": float(
                        group[
                            "predicted_probability"
                        ].mean()
                    ),
                }
            )

    # --------------------------------------------------------
    # Overall metrics
    # --------------------------------------------------------

    overall_metrics = {
        "threshold": BUSINESS_THRESHOLD,

        "accuracy": float(
            accuracy_score(
                y_holdout,
                predictions,
            )
        ),

        "precision": float(
            precision_score(
                y_holdout,
                predictions,
                zero_division=0,
            )
        ),

        "recall": float(
            recall_score(
                y_holdout,
                predictions,
                zero_division=0,
            )
        ),

        "f1": float(
            f1_score(
                y_holdout,
                predictions,
                zero_division=0,
            )
        ),

        "roc_auc": float(
            roc_auc_score(
                y_holdout,
                probabilities,
            )
        ),

        "true_negatives": int(tn),
        "false_positives": int(fp),
        "false_negatives": int(fn),
        "true_positives": int(tp),

        "false_negative_rate": (
            float(fn / (fn + tp))
            if (fn + tp) > 0
            else None
        ),

        "false_positive_rate": (
            float(fp / (fp + tn))
            if (fp + tn) > 0
            else None
        ),
    }

    report = {
        "overall_metrics": overall_metrics,
        "segment_analysis": segment_records,
        "segment_count": len(
            segment_records
        ),
    }

    return results, report


# ============================================================
# SHAP
# ============================================================

def normalize_shap_values(
    shap_values: Any,
    expected_rows: int,
    expected_features: int,
) -> np.ndarray:
    """
    Normalize SHAP output across SHAP versions.
    """

    if hasattr(
        shap_values,
        "values",
    ):
        values = shap_values.values
    else:
        values = shap_values

    # Some SHAP versions return a list.
    if isinstance(values, list):

        if len(values) == 2:
            values = values[1]

        elif len(values) == 1:
            values = values[0]

        else:
            raise ValueError(
                "Unexpected SHAP list output: "
                f"{len(values)} arrays."
            )

    values = np.asarray(values)

    # Standard:
    # rows x features
    if values.ndim == 2:

        normalized = values

    # Possible:
    # rows x features x classes
    elif values.ndim == 3:

        if values.shape[0] == expected_rows:

            if values.shape[1] == expected_features:
                normalized = values[:, :, -1]

            elif values.shape[2] == expected_features:
                normalized = values[:, -1, :]

            else:
                raise ValueError(
                    "Could not identify feature "
                    f"dimension in SHAP shape "
                    f"{values.shape}."
                )

        # Possible:
        # classes x rows x features
        elif (
            values.shape[1] == expected_rows
            and values.shape[2] == expected_features
        ):
            normalized = values[-1]

        else:
            raise ValueError(
                "Unexpected 3D SHAP shape: "
                f"{values.shape}"
            )

    else:
        raise ValueError(
            "Unexpected SHAP dimensions: "
            f"{values.ndim}"
        )

    if normalized.shape != (
        expected_rows,
        expected_features,
    ):
        raise ValueError(
            "Normalized SHAP shape mismatch. "
            f"Expected "
            f"{(expected_rows, expected_features)}, "
            f"got {normalized.shape}."
        )

    return normalized


def make_feature_frame(
    transformed: Any,
    feature_names: np.ndarray,
) -> pd.DataFrame:
    """Create a DataFrame from transformed model features."""

    if hasattr(
        transformed,
        "toarray",
    ):
        transformed = transformed.toarray()

    transformed = np.asarray(
        transformed
    )

    if transformed.ndim != 2:
        raise ValueError(
            "Expected a 2D transformed matrix, "
            f"got {transformed.shape}."
        )

    if (
        transformed.shape[1]
        != len(feature_names)
    ):
        raise ValueError(
            "Transformed feature count does not "
            "match feature names."
        )

    return pd.DataFrame(
        transformed,
        columns=feature_names,
    )


def build_local_explanations(
    X_holdout: pd.DataFrame,
    y_holdout: pd.Series,
    probabilities: np.ndarray,
    shap_matrix: np.ndarray,
    feature_names: np.ndarray,
) -> list[dict[str, Any]]:
    """Build three local SHAP explanations."""

    probabilities = np.asarray(
        probabilities,
        dtype=float,
    )

    # Highest-risk customer.
    highest_risk_index = int(
        np.argmax(probabilities)
    )

    # Customer closest to threshold.
    closest_threshold_index = int(
        np.argmin(
            np.abs(
                probabilities
                - BUSINESS_THRESHOLD
            )
        )
    )

    # Lowest-risk customer.
    lowest_risk_index = int(
        np.argmin(probabilities)
    )

    selected_indices = [
        highest_risk_index,
        closest_threshold_index,
        lowest_risk_index,
    ]

    # Remove duplicates while preserving order.
    selected_indices = list(
        dict.fromkeys(
            selected_indices
        )
    )

    records: list[dict[str, Any]] = []

    for number, row_index in enumerate(
        selected_indices,
        start=1,
    ):

        customer_row = X_holdout.iloc[
            row_index
        ]

        row_shap = shap_matrix[
            row_index
        ]

        ranking = np.argsort(
            np.abs(row_shap)
        )[::-1]

        top_indices = ranking[:10]

        contributions = []

        for feature_index in top_indices:

            value = float(
                row_shap[feature_index]
            )

            if value > 0:
                direction = (
                    "higher_churn_risk"
                )

            elif value < 0:
                direction = (
                    "lower_churn_risk"
                )

            else:
                direction = "neutral"

            contributions.append(
                {
                    "feature": str(
                        feature_names[
                            feature_index
                        ]
                    ),
                    "shap_value": value,
                    "absolute_shap_value": abs(
                        value
                    ),
                    "direction": direction,
                }
            )

        customer_features = {}

        for column in X_holdout.columns:

            value = customer_row[column]

            if pd.isna(value):
                customer_features[
                    column
                ] = None
            elif isinstance(
                value,
                np.generic,
            ):
                customer_features[
                    column
                ] = value.item()
            else:
                customer_features[
                    column
                ] = value

        records.append(
            {
                "explanation_number": number,
                "holdout_row_index": int(
                    row_index
                ),
                "predicted_probability": float(
                    probabilities[
                        row_index
                    ]
                ),
                "threshold": (
                    BUSINESS_THRESHOLD
                ),
                "predicted_class": int(
                    probabilities[
                        row_index
                    ]
                    >= BUSINESS_THRESHOLD
                ),
                "actual_class": int(
                    y_holdout.iloc[
                        row_index
                    ]
                ),
                "customer_features": (
                    customer_features
                ),
                "top_contributions": (
                    contributions
                ),
            }
        )

    return records


def explain_with_shap(
    model,
    X_holdout: pd.DataFrame,
    y_holdout: pd.Series,
    probabilities: np.ndarray,
) -> dict[str, Any]:
    """
    Generate global and local SHAP explanations.
    """

    # IMPORTANT:
    # The actual saved pipeline uses:
    #   preprocess
    #   model
    preprocess = model.named_steps[
        "preprocess"
    ]

    estimator = model.named_steps[
        "model"
    ]

    print(
        "      Transforming holdout "
        "through fitted preprocessor..."
    )

    transformed = preprocess.transform(
        X_holdout
    )

    if hasattr(
        transformed,
        "toarray",
    ):
        transformed_dense = (
            transformed.toarray()
        )
    else:
        transformed_dense = np.asarray(
            transformed
        )

    feature_names = np.asarray(
        preprocess.get_feature_names_out(),
        dtype=str,
    )

    if (
        transformed_dense.shape[1]
        != len(feature_names)
    ):
        raise ValueError(
            "Transformed feature count does not "
            "match preprocessing feature names."
        )

    feature_frame = make_feature_frame(
        transformed_dense,
        feature_names,
    )

    print(
        f"      Transformed feature matrix: "
        f"{transformed_dense.shape}"
    )

    print(
        "      Creating SHAP TreeExplainer..."
    )

    explainer = shap.TreeExplainer(
        estimator
    )

    print(
        "      Calculating SHAP values..."
    )

    shap_output = explainer.shap_values(
        transformed_dense
    )

    shap_matrix = normalize_shap_values(
        shap_output,
        expected_rows=len(X_holdout),
        expected_features=(
            transformed_dense.shape[1]
        ),
    )

    # --------------------------------------------------------
    # Global SHAP importance
    # --------------------------------------------------------

    mean_abs_shap = (
        np.abs(shap_matrix)
        .mean(axis=0)
    )

    global_importance = pd.DataFrame(
        {
            "feature": feature_names,
            "mean_abs_shap": (
                mean_abs_shap
            ),
        }
    )

    global_importance = (
        global_importance
        .sort_values(
            "mean_abs_shap",
            ascending=False,
        )
        .reset_index(drop=True)
    )

    global_importance["rank"] = (
        np.arange(
            1,
            len(global_importance) + 1,
        )
    )

    global_importance = (
        global_importance[
            [
                "rank",
                "feature",
                "mean_abs_shap",
            ]
        ]
    )

    global_importance.to_csv(
        SHAP_DIR
        / "global_feature_importance_v1.csv",
        index=False,
    )

    # --------------------------------------------------------
    # Local SHAP
    # --------------------------------------------------------

    local_explanations = (
        build_local_explanations(
            X_holdout=X_holdout,
            y_holdout=y_holdout,
            probabilities=probabilities,
            shap_matrix=shap_matrix,
            feature_names=feature_names,
        )
    )

    write_json(
        SHAP_DIR
        / "local_explanations_v1.json",
        local_explanations,
    )

    # Raw SHAP values.
    np.save(
        SHAP_DIR
        / "holdout_shap_values_v1.npy",
        shap_matrix,
    )

    # Transformed feature matrix.
    feature_frame.to_csv(
        SHAP_DIR
        / "holdout_transformed_features_v1.csv",
        index=False,
    )

    metadata = {
        "model": (
            "xgboost_tuned_cv_v1"
        ),
        "model_path": str(
            MODEL_PATH
        ),
        "holdout_rows": int(
            len(X_holdout)
        ),
        "transformed_feature_count": int(
            transformed_dense.shape[1]
        ),
        "threshold": (
            BUSINESS_THRESHOLD
        ),
        "local_explanation_count": (
            len(local_explanations)
        ),
        "local_holdout_indices": [
            record[
                "holdout_row_index"
            ]
            for record in (
                local_explanations
            )
        ],
        "explainer": "TreeExplainer",
        "causal_claim": False,
        "interpretation_note": (
            "SHAP values describe model "
            "contributions to the trained "
            "XGBoost prediction. They are "
            "not causal effects."
        ),
    }

    write_json(
        SHAP_DIR
        / "shap_metadata_v1.json",
        metadata,
    )

    return {
        "global_importance": (
            global_importance
        ),
        "local_explanations": (
            local_explanations
        ),
        "shap_matrix": shap_matrix,
        "feature_names": (
            feature_names.tolist()
        ),
        "metadata": metadata,
    }


# ============================================================
# MAIN
# ============================================================

def main() -> None:

    print("=" * 72)
    print(
        "ChurnGuard — Error Analysis + SHAP"
    )
    print("=" * 72)

    ensure_directories()

    # --------------------------------------------------------
    # 1. Dataset
    # --------------------------------------------------------

    print(
        "\n[1/7] Loading dataset..."
    )

    raw_df = load_raw_dataset()

    print(
        f"      Dataset shape: "
        f"{raw_df.shape}"
    )

    # --------------------------------------------------------
    # 2. Modeling frame
    # --------------------------------------------------------

    print(
        "\n[2/7] Preparing modeling frame..."
    )

    X, y = prepare_modeling_frame(
        raw_df
    )

    print(
        f"      Features: {X.shape[1]}"
    )

    print(
        f"      Samples: {len(X)}"
    )

    print(
        f"      Overall churn rate: "
        f"{y.mean():.4f}"
    )

    # --------------------------------------------------------
    # 3. Locked split
    # --------------------------------------------------------

    print(
        "\n[3/7] Reconstructing locked holdout..."
    )

    (
        X_train,
        X_holdout,
        y_train,
        y_holdout,
    ) = reconstruct_locked_holdout(
        X,
        y,
    )

    print(
        f"      Training rows: "
        f"{len(X_train)}"
    )

    print(
        f"      Holdout rows: "
        f"{len(X_holdout)}"
    )

    print(
        f"      Training churn rate: "
        f"{y_train.mean():.4f}"
    )

    print(
        f"      Holdout churn rate: "
        f"{y_holdout.mean():.4f}"
    )

    # --------------------------------------------------------
    # 4. Model
    # --------------------------------------------------------

    print(
        "\n[4/7] Loading tuned XGBoost pipeline..."
    )

    model = load_model()

    print(
        f"      Pipeline steps: "
        f"{list(model.named_steps.keys())}"
    )

    # --------------------------------------------------------
    # 5. Predictions
    # --------------------------------------------------------

    print(
        "\n[5/7] Generating locked holdout predictions..."
    )

    probabilities = model.predict_proba(
        X_holdout
    )[:, 1]

    predictions = (
        probabilities
        >= BUSINESS_THRESHOLD
    ).astype(int)

    print(
        f"      Business threshold: "
        f"{BUSINESS_THRESHOLD:.2f}"
    )

    print(
        f"      Predicted positive rate: "
        f"{predictions.mean():.4f}"
    )

    # --------------------------------------------------------
    # 6. Error analysis
    # --------------------------------------------------------

    print(
        "\n[6/7] Running error analysis..."
    )

    (
        holdout_results,
        error_report,
    ) = build_error_analysis(
        X_holdout,
        y_holdout,
        probabilities,
    )

    holdout_results.to_csv(
        ERROR_DIR
        / "holdout_error_analysis_v1.csv",
        index=True,
    )

    segment_df = pd.DataFrame(
        error_report[
            "segment_analysis"
        ]
    )

    segment_df.to_csv(
        ERROR_DIR
        / "segment_error_analysis_v1.csv",
        index=False,
    )

    write_json(
        ERROR_DIR
        / "error_analysis_report_v1.json",
        error_report,
    )

    metrics = error_report[
        "overall_metrics"
    ]

    print(
        f"      True negatives: "
        f"{metrics['true_negatives']}"
    )

    print(
        f"      False positives: "
        f"{metrics['false_positives']}"
    )

    print(
        f"      False negatives: "
        f"{metrics['false_negatives']}"
    )

    print(
        f"      True positives: "
        f"{metrics['true_positives']}"
    )

    print(
        f"      False-negative rate: "
        f"{metrics['false_negative_rate']:.4f}"
    )

    print(
        f"      False-positive rate: "
        f"{metrics['false_positive_rate']:.4f}"
    )

    print(
        f"      Segment groups analyzed: "
        f"{error_report['segment_count']}"
    )

    # --------------------------------------------------------
    # 7. SHAP
    # --------------------------------------------------------

    print(
        "\n[7/7] Running SHAP explanations..."
    )

    shap_report = explain_with_shap(
        model=model,
        X_holdout=X_holdout,
        y_holdout=y_holdout,
        probabilities=probabilities,
    )

    print(
        "      Global SHAP importance generated."
    )

    print(
        f"      Local explanations generated: "
        f"{len(shap_report['local_explanations'])}"
    )

    print(
        "\n      Top 10 global SHAP features:"
    )

    print(
        shap_report[
            "global_importance"
        ]
        .head(10)
        .to_string(index=False)
    )

    # --------------------------------------------------------
    # Final stage report
    # --------------------------------------------------------

    stage_report = {
        "stage": (
            "error_analysis_and_shap"
        ),
        "status": "PASS",
        "model": (
            "xgboost_tuned_cv_v1"
        ),
        "threshold": (
            BUSINESS_THRESHOLD
        ),

        "dataset": {
            "path": str(
                DATA_PATH
            ),
            "rows": int(
                len(raw_df)
            ),
            "features": int(
                X.shape[1]
            ),
        },

        "split": {
            "random_state": (
                RANDOM_STATE
            ),
            "holdout_size": (
                HOLDOUT_SIZE
            ),
            "train_rows": int(
                len(X_train)
            ),
            "holdout_rows": int(
                len(X_holdout)
            ),
            "train_churn_rate": float(
                y_train.mean()
            ),
            "holdout_churn_rate": float(
                y_holdout.mean()
            ),
        },

        "error_analysis": (
            error_report
        ),

        "shap": {
            "global_features": int(
                len(
                    shap_report[
                        "global_importance"
                    ]
                )
            ),
            "local_explanations": int(
                len(
                    shap_report[
                        "local_explanations"
                    ]
                )
            ),
            "explainer": (
                "TreeExplainer"
            ),
            "causal_claim": False,
        },

        "artifacts": [
            str(
                ERROR_DIR
                / "holdout_error_analysis_v1.csv"
            ),
            str(
                ERROR_DIR
                / "segment_error_analysis_v1.csv"
            ),
            str(
                ERROR_DIR
                / "error_analysis_report_v1.json"
            ),
            str(
                SHAP_DIR
                / "global_feature_importance_v1.csv"
            ),
            str(
                SHAP_DIR
                / "local_explanations_v1.json"
            ),
            str(
                SHAP_DIR
                / "holdout_shap_values_v1.npy"
            ),
            str(
                SHAP_DIR
                / "holdout_transformed_features_v1.csv"
            ),
            str(
                SHAP_DIR
                / "shap_metadata_v1.json"
            ),
        ],

        "notes": [
            (
                "The holdout split is reconstructed "
                "with the locked random seed."
            ),
            (
                "The business threshold remains "
                "fixed at 0.45."
            ),
            (
                "No candidate model was retrained "
                "during this stage."
            ),
            (
                "SHAP explanations describe model "
                "contributions and are not causal."
            ),
            (
                "The selected model is the tuned "
                "XGBoost candidate."
            ),
        ],
    }

    write_json(
        REPORT_DIR
        / "error_analysis_shap_report_v1.json",
        stage_report,
    )

    print(
        "\n" + "=" * 72
    )

    print(
        "STAGE PASS — Error Analysis + SHAP"
    )

    print(
        "=" * 72
    )

    print(
        "\nReports written to:"
    )

    print(
        f"  {ERROR_DIR}"
    )

    print(
        f"  {SHAP_DIR}"
    )

    print(
        "  "
        f"{REPORT_DIR / 'error_analysis_shap_report_v1.json'}"
    )


if __name__ == "__main__":
    main()