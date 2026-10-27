
from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import randint, uniform
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBClassifier


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "ml" / "data" / "WA_Fn-UseC_-Telco-Customer-Churn.csv"
REPORT_DIR = ROOT / "ml" / "reports"

# Start with a smoke test. Increase only after reviewing its runtime.
OUTER_FOLDS = 5
INNER_FOLDS = 5
N_ITER = 10
RANDOM_STATE = 2026
RECALL_FLOOR = 0.80
CALIBRATION_SIZE = 0.20

NUMERIC = ["tenure", "MonthlyCharges", "TotalCharges"]
TARGET = "Churn"
ID = "customerID"


def make_preprocessor(numeric, categorical, scale_numeric):
    numeric_steps = [("imputer", SimpleImputer(strategy="median"))]
    if scale_numeric:
        numeric_steps.append(("scaler", StandardScaler()))

    return ColumnTransformer([
        ("numeric", Pipeline(numeric_steps), numeric),
        ("categorical", Pipeline([
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=True)),
        ]), categorical),
    ], remainder="drop")


def make_searches(numeric, categorical, inner_cv, n_iter, seed):
    definitions = {}

    definitions["logistic_regression"] = (
        Pipeline([
            ("preprocess", make_preprocessor(numeric, categorical, True)),
            ("model", LogisticRegression(
                class_weight="balanced",
                solver="liblinear",
                max_iter=2000,
                random_state=seed,
            )),
        ]),
        {
            "model__C": uniform(0.01, 10.0),
            "model__penalty": ["l1", "l2"],
        },
    )

    definitions["random_forest"] = (
        Pipeline([
            ("preprocess", make_preprocessor(numeric, categorical, False)),
            ("model", RandomForestClassifier(
                class_weight="balanced_subsample",
                random_state=seed,
                n_jobs=1,
            )),
        ]),
        {
            "model__n_estimators": randint(200, 700),
            "model__max_depth": [None, 4, 6, 8, 12, 16, 20],
            "model__min_samples_split": randint(2, 20),
            "model__min_samples_leaf": randint(1, 10),
            "model__max_features": ["sqrt", "log2", None],
            "model__class_weight": ["balanced", "balanced_subsample"],
        },
    )

    definitions["xgboost"] = (
        Pipeline([
            ("preprocess", make_preprocessor(numeric, categorical, False)),
            ("model", XGBClassifier(
                objective="binary:logistic",
                eval_metric="logloss",
                tree_method="hist",
                random_state=seed,
                n_jobs=1,
                verbosity=0,
            )),
        ]),
        {
            "model__n_estimators": randint(150, 600),
            "model__max_depth": randint(2, 8),
            "model__learning_rate": uniform(0.02, 0.18),
            "model__subsample": uniform(0.65, 0.35),
            "model__colsample_bytree": uniform(0.65, 0.35),
            "model__min_child_weight": randint(1, 12),
            "model__gamma": uniform(0.0, 0.5),
            "model__reg_alpha": uniform(0.0, 1.0),
            "model__reg_lambda": uniform(0.5, 3.0),
            "model__scale_pos_weight": uniform(1.5, 2.5),
        },
    )

    return {
        name: RandomizedSearchCV(
            estimator=pipeline,
            param_distributions=params,
            n_iter=n_iter,
            scoring="average_precision",
            cv=inner_cv,
            refit=True,
            random_state=seed,
            n_jobs=1,
            verbose=0,
            return_train_score=False,
        )
        for name, (pipeline, params) in definitions.items()
    }


def choose_threshold(y_true, probabilities):
    candidates = np.unique(np.concatenate([
        np.linspace(0.05, 0.95, 181),
        np.asarray([0.5]),
    ]))
    rows = []

    for threshold in candidates:
        predictions = (probabilities >= threshold).astype(int)
        rows.append({
            "threshold": float(threshold),
            "recall": recall_score(y_true, predictions, zero_division=0),
            "precision": precision_score(y_true, predictions, zero_division=0),
            "f1": f1_score(y_true, predictions, zero_division=0),
        })

    eligible = [r for r in rows if r["recall"] >= RECALL_FLOOR]
    if eligible:
        return max(eligible, key=lambda r: (r["f1"], r["threshold"]))

    # The requested recall floor was unattainable on calibration data.
    return max(rows, key=lambda r: (r["recall"], r["f1"], r["threshold"]))


def main():
    started = time.time()
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    metrics_path = REPORT_DIR / "nested_cv_threshold_fold_metrics_v1.csv"
    oof_path = REPORT_DIR / "nested_cv_oof_predictions_v1.csv"
    sensitivity_path = REPORT_DIR / "nested_cv_threshold_sensitivity_v1.csv"
    summary_path = REPORT_DIR / "nested_cv_threshold_analysis_v1.json"

    output_paths = [metrics_path, oof_path, sensitivity_path, summary_path]
    if any(path.exists() for path in output_paths):
        raise FileExistsError("A threshold-analysis output exists; nothing overwritten.")

    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)
    required = {ID, TARGET, *NUMERIC}
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"Required columns missing: {missing}")
    if df[ID].isna().any() or df[ID].duplicated().any():
        raise ValueError("Customer IDs are missing or duplicated.")
    if set(df[TARGET].astype(str).unique()) != {"Yes", "No"}:
        raise ValueError("Unexpected target values.")

    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
    X = df.drop(columns=[ID, TARGET]).copy()
    y = df[TARGET].map({"No": 0, "Yes": 1}).astype(int)
    categorical = [c for c in X.columns if c not in NUMERIC]

    if len(X.columns) != 19:
        raise ValueError(f"Expected 19 features, found {len(X.columns)}")

    outer_cv = StratifiedKFold(
        n_splits=OUTER_FOLDS, shuffle=True, random_state=RANDOM_STATE
    )
    results = []
    selected_models = []
    oof_predictions = []

    print(f"Rows: {len(X)} | Features: {X.shape[1]}")
    print(
        f"Rigorous nested CV: {OUTER_FOLDS} outer folds, "
        f"{INNER_FOLDS} inner folds, {N_ITER} configurations/model"
    )
    print(f"Calibration share of each outer training fold: {CALIBRATION_SIZE:.0%}")
    print("Existing models and reports will not be overwritten.")

    for fold, (train_idx, test_idx) in enumerate(outer_cv.split(X, y), start=1):
        print(f"\nOuter fold {fold}/{OUTER_FOLDS}")
        X_outer_train = X.iloc[train_idx]
        y_outer_train = y.iloc[train_idx]
        X_test = X.iloc[test_idx]
        y_test = y.iloc[test_idx]

        # Calibration rows are not used to tune or fit the selected model.
        X_fit, X_cal, y_fit, y_cal = train_test_split(
            X_outer_train,
            y_outer_train,
            test_size=CALIBRATION_SIZE,
            random_state=RANDOM_STATE + 1000 + fold,
            stratify=y_outer_train,
        )

        inner_cv = StratifiedKFold(
            n_splits=INNER_FOLDS,
            shuffle=True,
            random_state=RANDOM_STATE + fold,
        )
        searches = make_searches(
            NUMERIC, categorical, inner_cv, N_ITER, RANDOM_STATE + fold
        )

        fitted = {}
        for name, search in searches.items():
            print(f"  Tuning {name} on model-fitting rows...")
            search.fit(X_fit, y_fit)
            fitted[name] = search
            print(f"    Inner-CV average precision: {search.best_score_:.4f}")

        selected_name, selected_search = max(
            fitted.items(), key=lambda item: item[1].best_score_
        )
        selected_models.append(selected_name)
        selected_model = selected_search.best_estimator_
        print(f"  Selected model: {selected_name}")

        # The model has never seen calibration rows or their labels.
        calibration_probabilities = selected_model.predict_proba(X_cal)[:, 1]
        threshold_info = choose_threshold(
            y_cal.to_numpy(), calibration_probabilities
        )
        threshold = threshold_info["threshold"]

        # Outer test data is used only for final fold evaluation.
        test_probabilities = selected_model.predict_proba(X_test)[:, 1]
        test_predictions = (test_probabilities >= threshold).astype(int)
        for row_idx, actual, probability in zip(test_idx, y_test.to_numpy(), test_probabilities):
            oof_predictions.append({
                "row_index": int(row_idx),
                "customerID": str(df.iloc[row_idx][ID]),
                "actual_churn": int(actual),
                "probability": float(probability),
                "outer_fold": int(fold),
                "selected_model": selected_name,
            })

        row = {
            "outer_fold": fold,
            "model_fit_rows": int(len(X_fit)),
            "threshold_calibration_rows": int(len(X_cal)),
            "test_rows": int(len(X_test)),
            "selected_model": selected_name,
            "inner_cv_average_precision": float(selected_search.best_score_),
            "selected_threshold": float(threshold),
            "calibration_recall": float(threshold_info["recall"]),
            "calibration_precision": float(threshold_info["precision"]),
            "calibration_f1": float(threshold_info["f1"]),
            "test_accuracy": float(accuracy_score(y_test, test_predictions)),
            "test_precision": float(precision_score(y_test, test_predictions, zero_division=0)),
            "test_recall": float(recall_score(y_test, test_predictions, zero_division=0)),
            "test_f1": float(f1_score(y_test, test_predictions, zero_division=0)),
            "test_roc_auc": float(roc_auc_score(y_test, test_probabilities)),
            "test_average_precision": float(average_precision_score(y_test, test_probabilities)),
        }
        results.append(row)
        print(
            f"  Test AP={row['test_average_precision']:.4f}, "
            f"F1={row['test_f1']:.4f}, recall={row['test_recall']:.4f}, "
            f"threshold={threshold:.3f}"
        )

    results_df = pd.DataFrame(results)
    results_df.to_csv(metrics_path, index=False)

    oof_df = pd.DataFrame(oof_predictions)
    if len(oof_df) != len(df) or oof_df["row_index"].duplicated().any():
        raise ValueError("Expected exactly one out-of-fold prediction per dataset row.")
    oof_df.to_csv(oof_path, index=False)

    actual = oof_df["actual_churn"].to_numpy(dtype=int)
    probabilities = oof_df["probability"].to_numpy(dtype=float)
    threshold_rows = []
    candidates = np.unique(np.concatenate([np.linspace(0.05, 0.95, 181), [0.5]]))
    for candidate in candidates:
        predicted = (probabilities >= candidate).astype(int)
        tn = int(((actual == 0) & (predicted == 0)).sum())
        fp = int(((actual == 0) & (predicted == 1)).sum())
        fn = int(((actual == 1) & (predicted == 0)).sum())
        tp = int(((actual == 1) & (predicted == 1)).sum())
        rec = recall_score(actual, predicted, zero_division=0)
        threshold_rows.append({
            "threshold": float(candidate),
            "accuracy": float(accuracy_score(actual, predicted)),
            "precision": float(precision_score(actual, predicted, zero_division=0)),
            "recall": float(rec),
            "f1": float(f1_score(actual, predicted, zero_division=0)),
            "predicted_positive_rate": float(predicted.mean()),
            "true_positive": tp, "true_negative": tn,
            "false_positive": fp, "false_negative": fn,
            "meets_recall_floor": bool(rec >= RECALL_FLOOR),
        })
    pd.DataFrame(threshold_rows).to_csv(sensitivity_path, index=False)

    metric_columns = [
        "test_accuracy", "test_precision", "test_recall", "test_f1",
        "test_roc_auc", "test_average_precision",
    ]
    summary = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "dataset": DATA_PATH.name,
        "rows": int(len(df)),
        "features": int(X.shape[1]),
        "positive_label": "Yes",
        "positive_class_rate": float(y.mean()),
        "method": "Outer stratified CV with inner model selection and separate calibration split",
        "outer_folds": OUTER_FOLDS,
        "inner_folds": INNER_FOLDS,
        "randomized_configurations_per_model_per_outer_fold": N_ITER,
        "calibration_size_fraction_of_outer_training_data": CALIBRATION_SIZE,
        "primary_inner_selection_metric": "average_precision",
        "threshold_selection": (
            "Threshold selected on a stratified calibration subset excluded from "
            "model tuning and fitting; maximize F1 subject to recall >= 0.80 "
            "where feasible, with higher threshold as tie-break."
        ),
        "outer_test_used_for_model_or_threshold_selection": False,
        "outer_fold_selected_models": selected_models,
        "mean_outer_test_metrics": {
            col: float(results_df[col].mean()) for col in metric_columns
        },
        "std_outer_test_metrics": {
            col: float(results_df[col].std(ddof=1)) for col in metric_columns
        },
        "interpretation_warning": (
            "Cross-validation estimates only. The historical holdout has already "
            "influenced earlier model and threshold choices. This is not a new "
            "untouched holdout evaluation. Each fold fits on fewer rows because "
            "a separate calibration subset is reserved for threshold selection."
        ),
        "elapsed_seconds": round(time.time() - started, 2),
    }

    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\nThreshold sensitivity analysis completed.")
    print(f"Fold metrics: {metrics_path}")
    print(f"OOF predictions: {oof_path}")
    print(f"Threshold sensitivity: {sensitivity_path}")
    print(f"Summary: {summary_path}")
    print("\nMean outer-test metrics:")
    print(results_df[metric_columns].mean().to_string())


if __name__ == "__main__":
    main()

