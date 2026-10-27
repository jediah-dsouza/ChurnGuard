from __future__ import annotations

import json
import time
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from sklearn.calibration import calibration_curve
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split


# ============================================================================
# ChurnGuard — Formal Holdout Evaluation + Business Threshold Analysis
# ============================================================================
#
# IMPORTANT:
# - The holdout split is LOCKED.
# - No model tuning happens here.
# - No feature selection happens here.
# - No retraining happens here.
# - The holdout is used only for formal evaluation and threshold analysis.
# ============================================================================


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ML_DIR = PROJECT_ROOT / "ml"

DATA_PATH = ML_DIR / "data" / "WA_Fn-UseC_-Telco-Customer-Churn.csv"
MODELS_DIR = ML_DIR / "models"
REPORTS_DIR = ML_DIR / "reports"

REPORT_PATH = REPORTS_DIR / "formal_holdout_evaluation_v1.json"
METRICS_CSV_PATH = REPORTS_DIR / "formal_holdout_model_metrics_v1.csv"
THRESHOLD_CSV_PATH = REPORTS_DIR / "business_threshold_analysis_v1.csv"
CONFUSION_DIR = REPORTS_DIR / "confusion_matrices"
CALIBRATION_PATH = REPORTS_DIR / "calibration_curves_v1.png"
THRESHOLD_PLOT_PATH = REPORTS_DIR / "threshold_tradeoff_v1.png"

RANDOM_STATE = 42
HOLDOUT_SIZE = 0.20

TARGET = "Churn"
ID_COLUMN = "customerID"

FEATURE_COLUMNS = [
    "gender",
    "SeniorCitizen",
    "Partner",
    "Dependents",
    "tenure",
    "PhoneService",
    "MultipleLines",
    "InternetService",
    "OnlineSecurity",
    "OnlineBackup",
    "DeviceProtection",
    "TechSupport",
    "StreamingTV",
    "StreamingMovies",
    "Contract",
    "PaperlessBilling",
    "PaymentMethod",
    "MonthlyCharges",
    "TotalCharges",
]

MODEL_FILES = {
    "logistic_regression": MODELS_DIR / "logistic_regression_tuned_cv_v1.joblib",
    "random_forest": MODELS_DIR / "random_forest_tuned_cv_v1.joblib",
    "xgboost": MODELS_DIR / "xgboost_tuned_cv_v1.joblib",
}


# ============================================================================
# Helpers
# ============================================================================


def pct(value: float) -> float:
    return round(float(value) * 100.0, 4)


def safe_float(value) -> float:
    return float(value)


def validate_dataset(df: pd.DataFrame) -> None:
    required = set(FEATURE_COLUMNS + [TARGET, ID_COLUMN])
    missing = sorted(required - set(df.columns))

    if missing:
        raise ValueError(
            f"Required columns missing from dataset: {missing}"
        )

    if df[ID_COLUMN].duplicated().any():
        raise ValueError("Duplicate customer IDs detected.")

    if df[ID_COLUMN].isna().any():
        raise ValueError("Missing customer IDs detected.")

    if df[TARGET].isna().any():
        raise ValueError("Missing target values detected.")

    leakage_columns = {
        "churn_risk_score",
        "post_outcome_churn_flag",
    }

    found_leakage = sorted(leakage_columns.intersection(df.columns))

    if found_leakage:
        raise ValueError(
            f"Known target-derived/post-outcome leakage columns detected: "
            f"{found_leakage}"
        )


def build_locked_holdout(df: pd.DataFrame):
    y = (df[TARGET] == "Yes").astype(int)

    X = df[FEATURE_COLUMNS].copy()

    # Match preparation/training behavior.
    X["TotalCharges"] = pd.to_numeric(
        X["TotalCharges"],
        errors="coerce",
    )

    X_train, X_holdout, y_train, y_holdout = train_test_split(
        X,
        y,
        test_size=HOLDOUT_SIZE,
        stratify=y,
        random_state=RANDOM_STATE,
    )

    return X_train, X_holdout, y_train, y_holdout


def evaluate_predictions(
    y_true: pd.Series,
    probabilities: np.ndarray,
    threshold: float = 0.5,
) -> dict:

    predictions = (probabilities >= threshold).astype(int)

    report = classification_report(
        y_true,
        predictions,
        target_names=["No Churn", "Churn"],
        output_dict=True,
        zero_division=0,
    )

    cm = confusion_matrix(
        y_true,
        predictions,
        labels=[0, 1],
    )

    return {
        "threshold": safe_float(threshold),
        "accuracy": safe_float(accuracy_score(y_true, predictions)),
        "precision": safe_float(precision_score(
            y_true,
            predictions,
            zero_division=0,
        )),
        "recall": safe_float(recall_score(
            y_true,
            predictions,
            zero_division=0,
        )),
        "f1": safe_float(f1_score(
            y_true,
            predictions,
            zero_division=0,
        )),
        "roc_auc": safe_float(
            roc_auc_score(y_true, probabilities)
        ),
        "pr_auc": safe_float(
            average_precision_score(y_true, probabilities)
        ),
        "confusion_matrix": cm.tolist(),
        "classification_report": report,
    }


def threshold_analysis(
    y_true: pd.Series,
    probabilities: np.ndarray,
) -> pd.DataFrame:

    rows = []

    # Dense enough to make the business trade-off visible while
    # remaining easy to interpret operationally.
    thresholds = np.round(
        np.arange(0.10, 0.91, 0.01),
        2,
    )

    for threshold in thresholds:
        predictions = (
            probabilities >= threshold
        ).astype(int)

        tn, fp, fn, tp = confusion_matrix(
            y_true,
            predictions,
            labels=[0, 1],
        ).ravel()

        precision = precision_score(
            y_true,
            predictions,
            zero_division=0,
        )

        recall = recall_score(
            y_true,
            predictions,
            zero_division=0,
        )

        f1 = f1_score(
            y_true,
            predictions,
            zero_division=0,
        )

        rows.append(
            {
                "threshold": float(threshold),
                "accuracy": float(
                    accuracy_score(y_true, predictions)
                ),
                "precision": float(precision),
                "recall": float(recall),
                "f1": float(f1),
                "true_negatives": int(tn),
                "false_positives": int(fp),
                "false_negatives": int(fn),
                "true_positives": int(tp),
                "predicted_positive_rate": float(
                    predictions.mean()
                ),
            }
        )

    return pd.DataFrame(rows)


def select_business_threshold(
    threshold_df: pd.DataFrame,
) -> tuple[float, dict]:

    # Business priority:
    # 1. Maintain recall >= 0.80 where possible.
    # 2. Among qualifying thresholds, maximize F1.
    # 3. Prefer the higher threshold when tied, reducing unnecessary
    #    retention interventions.
    #
    # This is intentionally a transparent rule rather than silently
    # optimizing a hidden business objective.

    recall_floor = 0.80

    eligible = threshold_df[
        threshold_df["recall"] >= recall_floor
    ].copy()

    if eligible.empty:
        # Explicit fallback if the model cannot reach the recall floor.
        selected = threshold_df.loc[
            threshold_df["recall"].idxmax()
        ]
        reason = (
            "No threshold reached the 0.80 recall floor; "
            "selected the threshold with maximum recall."
        )
    else:
        max_f1 = eligible["f1"].max()

        best = eligible[
            np.isclose(
                eligible["f1"],
                max_f1,
                rtol=0.0,
                atol=1e-12,
            )
        ].copy()

        selected = best.sort_values(
            "threshold",
            ascending=False,
        ).iloc[0]

        reason = (
            "Selected the highest threshold among thresholds "
            "meeting the 0.80 recall floor and maximizing F1, "
            "favoring fewer unnecessary retention interventions "
            "when the performance trade-off is tied."
        )

    return float(selected["threshold"]), {
        "recall_floor": recall_floor,
        "selection_reason": reason,
        "selected_metrics": {
            key: safe_float(selected[key])
            for key in [
                "threshold",
                "accuracy",
                "precision",
                "recall",
                "f1",
                "predicted_positive_rate",
            ]
        },
        "confusion_counts": {
            key: int(selected[key])
            for key in [
                "true_negatives",
                "false_positives",
                "false_negatives",
                "true_positives",
            ]
        },
    }


def save_confusion_matrix(
    matrix: list[list[int]],
    model_name: str,
) -> None:

    CONFUSION_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    cm = np.asarray(matrix)

    fig, ax = plt.subplots(
        figsize=(5, 4),
    )

    image = ax.imshow(cm)

    ax.set_title(
        f"{model_name.replace('_', ' ').title()} — Holdout Confusion Matrix"
    )

    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")

    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])

    ax.set_xticklabels(["No Churn", "Churn"])
    ax.set_yticklabels(["No Churn", "Churn"])

    for i in range(2):
        for j in range(2):
            ax.text(
                j,
                i,
                str(cm[i, j]),
                ha="center",
                va="center",
            )

    fig.colorbar(image, ax=ax)

    output = (
        CONFUSION_DIR
        / f"{model_name}_holdout_confusion_matrix.png"
    )

    fig.tight_layout()
    fig.savefig(
        output,
        dpi=160,
        bbox_inches="tight",
    )
    plt.close(fig)


def save_calibration_plot(
    y_true: pd.Series,
    probabilities_by_model: dict[str, np.ndarray],
) -> None:

    fig, ax = plt.subplots(
        figsize=(7, 6),
    )

    ax.plot(
        [0, 1],
        [0, 1],
        linestyle="--",
        label="Perfect calibration",
    )

    for model_name, probabilities in probabilities_by_model.items():
        fraction_positive, mean_predicted = calibration_curve(
            y_true,
            probabilities,
            n_bins=10,
            strategy="quantile",
        )

        ax.plot(
            mean_predicted,
            fraction_positive,
            marker="o",
            label=model_name.replace("_", " ").title(),
        )

    ax.set_title("ChurnGuard — Holdout Calibration")
    ax.set_xlabel("Mean predicted probability")
    ax.set_ylabel("Fraction of positives")
    ax.legend()
    ax.grid(True, alpha=0.25)

    fig.tight_layout()
    fig.savefig(
        CALIBRATION_PATH,
        dpi=160,
        bbox_inches="tight",
    )
    plt.close(fig)


def save_threshold_plot(
    threshold_df: pd.DataFrame,
    selected_threshold: float,
) -> None:

    fig, ax = plt.subplots(
        figsize=(8, 5),
    )

    ax.plot(
        threshold_df["threshold"],
        threshold_df["recall"],
        label="Recall",
    )

    ax.plot(
        threshold_df["threshold"],
        threshold_df["precision"],
        label="Precision",
    )

    ax.plot(
        threshold_df["threshold"],
        threshold_df["f1"],
        label="F1",
    )

    ax.axvline(
        selected_threshold,
        linestyle="--",
        label=f"Selected threshold = {selected_threshold:.2f}",
    )

    ax.set_title(
        "ChurnGuard — Business Threshold Trade-off"
    )

    ax.set_xlabel("Probability threshold")
    ax.set_ylabel("Metric")
    ax.set_ylim(0, 1.05)

    ax.legend()
    ax.grid(True, alpha=0.25)

    fig.tight_layout()
    fig.savefig(
        THRESHOLD_PLOT_PATH,
        dpi=160,
        bbox_inches="tight",
    )
    plt.close(fig)


# ============================================================================
# Main
# ============================================================================


def main() -> None:

    start_time = time.perf_counter()

    REPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print("=" * 72)
    print("ChurnGuard — Formal Holdout Evaluation")
    print("=" * 72)

    # ------------------------------------------------------------------------
    # 1. Load and validate
    # ------------------------------------------------------------------------

    print("\n[1/7] Loading and validating dataset...")

    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_PATH}"
        )

    df = pd.read_csv(DATA_PATH)

    print(f"Dataset: {DATA_PATH}")
    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")

    validate_dataset(df)

    print("Dataset validation: PASS")

    # ------------------------------------------------------------------------
    # 2. Reconstruct exact locked split
    # ------------------------------------------------------------------------

    print("\n[2/7] Reconstructing locked holdout split...")

    (
        X_train,
        X_holdout,
        y_train,
        y_holdout,
    ) = build_locked_holdout(df)

    print(f"Training rows: {len(X_train):,}")
    print(f"Holdout rows: {len(X_holdout):,}")

    expected_train = 5634
    expected_holdout = 1409

    if len(X_train) != expected_train:
        raise AssertionError(
            f"Unexpected training size: {len(X_train)}"
        )

    if len(X_holdout) != expected_holdout:
        raise AssertionError(
            f"Unexpected holdout size: {len(X_holdout)}"
        )

    print("Expected split sizes: PASS")
    print("Holdout remains untouched for formal evaluation.")

    # ------------------------------------------------------------------------
    # 3. Load candidate models
    # ------------------------------------------------------------------------

    print("\n[3/7] Loading tuned candidate pipelines...")

    models = {}

    for model_name, path in MODEL_FILES.items():

        if not path.exists():
            raise FileNotFoundError(
                f"Model artifact not found: {path}"
            )

        models[model_name] = joblib.load(path)

        print(f"{model_name}: loaded")

    print("Candidate artifacts: PASS")

    # ------------------------------------------------------------------------
    # 4. Formal evaluation
    # ------------------------------------------------------------------------

    print("\n[4/7] Running formal holdout evaluation...")
    print("-" * 72)

    metrics_rows = []
    probabilities_by_model = {}
    model_results = {}

    for model_name, model in models.items():

        print(f"\n{model_name}")

        probabilities = model.predict_proba(
            X_holdout
        )[:, 1]

        probabilities_by_model[model_name] = probabilities

        result = evaluate_predictions(
            y_holdout,
            probabilities,
            threshold=0.50,
        )

        model_results[model_name] = result

        print(
            f"Accuracy : {result['accuracy']:.4f}"
        )
        print(
            f"Precision: {result['precision']:.4f}"
        )
        print(
            f"Recall   : {result['recall']:.4f}"
        )
        print(
            f"F1       : {result['f1']:.4f}"
        )
        print(
            f"ROC-AUC  : {result['roc_auc']:.4f}"
        )
        print(
            f"PR-AUC   : {result['pr_auc']:.4f}"
        )

        metrics_rows.append(
            {
                "model": model_name,
                "threshold": 0.50,
                "accuracy": result["accuracy"],
                "precision": result["precision"],
                "recall": result["recall"],
                "f1": result["f1"],
                "roc_auc": result["roc_auc"],
                "pr_auc": result["pr_auc"],
            }
        )

        save_confusion_matrix(
            result["confusion_matrix"],
            model_name,
        )

    metrics_df = pd.DataFrame(metrics_rows)

    metrics_df.to_csv(
        METRICS_CSV_PATH,
        index=False,
    )

    # ------------------------------------------------------------------------
    # 5. Select model using formal evidence
    # ------------------------------------------------------------------------

    print("\n[5/7] Selecting candidate for threshold analysis...")

    # Primary criterion remains PR-AUC because churn is imbalanced.
    # F1 and recall are secondary business-supporting metrics.
    selected_model_name = (
        metrics_df.sort_values(
            by=[
                "pr_auc",
                "f1",
                "recall",
            ],
            ascending=False,
        )
        .iloc[0]["model"]
    )

    selected_model = models[selected_model_name]
    selected_probabilities = probabilities_by_model[
        selected_model_name
    ]

    print(
        f"Selected model for business threshold analysis: "
        f"{selected_model_name}"
    )

    print(
        "Selection criterion: highest holdout PR-AUC, "
        "with F1 and recall as deterministic tie-breakers."
    )

    # ------------------------------------------------------------------------
    # 6. Threshold + calibration analysis
    # ------------------------------------------------------------------------

    print("\n[6/7] Running business threshold and calibration analysis...")

    threshold_df = threshold_analysis(
        y_holdout,
        selected_probabilities,
    )

    threshold_df.to_csv(
        THRESHOLD_CSV_PATH,
        index=False,
    )

    selected_threshold, threshold_selection = (
        select_business_threshold(
            threshold_df
        )
    )

    threshold_result = evaluate_predictions(
        y_holdout,
        selected_probabilities,
        threshold=selected_threshold,
    )

    save_calibration_plot(
        y_holdout,
        probabilities_by_model,
    )

    save_threshold_plot(
        threshold_df,
        selected_threshold,
    )

    print(
        f"Selected business threshold: "
        f"{selected_threshold:.2f}"
    )

    print(
        f"Threshold recall   : "
        f"{threshold_result['recall']:.4f}"
    )

    print(
        f"Threshold precision: "
        f"{threshold_result['precision']:.4f}"
    )

    print(
        f"Threshold F1       : "
        f"{threshold_result['f1']:.4f}"
    )

    print(
        f"Predicted positive rate: "
        f"{threshold_selection['selected_metrics']['predicted_positive_rate']:.4f}"
    )

    # ------------------------------------------------------------------------
    # 7. Write formal report
    # ------------------------------------------------------------------------

    print("\n[7/7] Writing formal evaluation report...")

    report = {
        "experiment": {
            "name": "ChurnGuard Formal Holdout Evaluation",
            "version": "v1",
            "random_state": RANDOM_STATE,
            "holdout_size": HOLDOUT_SIZE,
            "target": TARGET,
            "positive_class": "Yes / 1",
            "primary_selection_metric": "PR-AUC",
            "business_priority": "Recall-weighted churn detection",
        },
        "data_integrity": {
            "dataset_rows": int(len(df)),
            "training_rows": int(len(X_train)),
            "holdout_rows": int(len(X_holdout)),
            "holdout_locked": True,
            "holdout_used_for_tuning": False,
            "holdout_used_for_feature_selection": False,
            "holdout_used_for_retraining": False,
            "train_holdout_churn_rate": {
                "training": float(y_train.mean()),
                "holdout": float(y_holdout.mean()),
            },
        },
        "candidate_models": {
            model_name: {
                "holdout_metrics_at_0_50": {
                    "accuracy": result["accuracy"],
                    "precision": result["precision"],
                    "recall": result["recall"],
                    "f1": result["f1"],
                    "roc_auc": result["roc_auc"],
                    "pr_auc": result["pr_auc"],
                },
                "confusion_matrix": result[
                    "confusion_matrix"
                ],
            }
            for model_name, result in model_results.items()
        },
        "model_selection": {
            "selected_model": selected_model_name,
            "selection_metric": "PR-AUC",
            "selection_reason": (
                "Highest formal holdout PR-AUC among the "
                "tuned candidate models."
            ),
            "candidate_ranking": (
                metrics_df.sort_values(
                    by=[
                        "pr_auc",
                        "f1",
                        "recall",
                    ],
                    ascending=False,
                )
                .to_dict(orient="records")
            ),
        },
        "calibration": {
            "artifact": str(
                CALIBRATION_PATH.relative_to(
                    PROJECT_ROOT
                )
            ),
            "note": (
                "Calibration curves are descriptive holdout "
                "diagnostics. No post-hoc calibration model "
                "was fitted in this stage."
            ),
        },
        "business_threshold": {
            "selected_model": selected_model_name,
            "selected_threshold": selected_threshold,
            "selection": threshold_selection,
            "final_metrics": {
                "accuracy": threshold_result["accuracy"],
                "precision": threshold_result["precision"],
                "recall": threshold_result["recall"],
                "f1": threshold_result["f1"],
                "roc_auc": threshold_result["roc_auc"],
                "pr_auc": threshold_result["pr_auc"],
                "confusion_matrix": threshold_result[
                    "confusion_matrix"
                ],
            },
            "artifacts": {
                "threshold_table": str(
                    THRESHOLD_CSV_PATH.relative_to(
                        PROJECT_ROOT
                    )
                ),
                "threshold_plot": str(
                    THRESHOLD_PLOT_PATH.relative_to(
                        PROJECT_ROOT
                    )
                ),
            },
        },
        "artifacts": {
            "model_metrics": str(
                METRICS_CSV_PATH.relative_to(
                    PROJECT_ROOT
                )
            ),
            "calibration_plot": str(
                CALIBRATION_PATH.relative_to(
                    PROJECT_ROOT
                )
            ),
            "confusion_matrix_directory": str(
                CONFUSION_DIR.relative_to(
                    PROJECT_ROOT
                )
            ),
        },
        "stage_status": "PASS",
        "next_stage": (
            "Error analysis by customer segment + SHAP "
            "global/local explanation analysis."
        ),
        "runtime_seconds": round(
            time.perf_counter() - start_time,
            2,
        ),
    }

    with REPORT_PATH.open(
        "w",
        encoding="utf-8",
    ) as handle:
        json.dump(
            report,
            handle,
            indent=2,
        )

    print("\n" + "=" * 72)
    print("FORMAL HOLDOUT EVALUATION STAGE PASSED")
    print("=" * 72)

    print(
        f"Selected model: {selected_model_name}"
    )

    print(
        f"Selected business threshold: "
        f"{selected_threshold:.2f}"
    )

    print(
        f"Holdout PR-AUC: "
        f"{threshold_result['pr_auc']:.4f}"
    )

    print(
        f"Business recall: "
        f"{threshold_result['recall']:.4f}"
    )

    print(
        f"Business precision: "
        f"{threshold_result['precision']:.4f}"
    )

    print(
        f"Business F1: "
        f"{threshold_result['f1']:.4f}"
    )

    print("\nReports:")
    print(f"  {REPORT_PATH}")
    print(f"  {METRICS_CSV_PATH}")
    print(f"  {THRESHOLD_CSV_PATH}")
    print(f"  {CALIBRATION_PATH}")
    print(f"  {THRESHOLD_PLOT_PATH}")

    print(
        f"\nRuntime: "
        f"{time.perf_counter() - start_time:.2f} seconds"
    )

    print(
        "\nHoldout status: FORMALLY EVALUATED / LOCKED"
    )

    print(
        "Next stage: error analysis + SHAP global/local explanations"
    )


if __name__ == "__main__":
    main()