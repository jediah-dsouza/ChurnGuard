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
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBClassifier


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "ml" / "data" / "WA_Fn-UseC_-Telco-Customer-Churn.csv"
REPORT_DIR = ROOT / "ml" / "reports"

# Start with a small smoke test. Increase these only after it succeeds.
OUTER_FOLDS = 3
INNER_FOLDS = 3
N_ITER = 2
RANDOM_STATE = 2026
RECALL_FLOOR = 0.80

NUMERIC = ["tenure", "MonthlyCharges", "TotalCharges"]
TARGET = "Churn"
ID = "customerID"


def make_preprocessor(numeric, categorical, scale_numeric):
    numeric_steps = [("imputer", SimpleImputer(strategy="median"))]
    if scale_numeric:
        numeric_steps.append(("scaler", StandardScaler()))

    numeric_pipe = Pipeline(numeric_steps)
    categorical_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=True)),
    ])

    return ColumnTransformer([
        ("numeric", numeric_pipe, numeric),
        ("categorical", categorical_pipe, categorical),
    ], remainder="drop")


def make_searches(numeric, categorical, inner_cv, n_iter, seed):
    searches = {}

    lr = Pipeline([
        ("preprocess", make_preprocessor(numeric, categorical, True)),
        ("model", LogisticRegression(
            class_weight="balanced",
            solver="liblinear",
            max_iter=2000,
            random_state=seed,
        )),
    ])
    searches["logistic_regression"] = (
        lr,
        {
            "model__C": uniform(0.01, 10.0),
            "model__penalty": ["l1", "l2"],
        },
    )

    rf = Pipeline([
        ("preprocess", make_preprocessor(numeric, categorical, False)),
        ("model", RandomForestClassifier(
            class_weight="balanced_subsample",
            random_state=seed,
            n_jobs=1,
        )),
    ])
    searches["random_forest"] = (
        rf,
        {
            "model__n_estimators": randint(200, 700),
            "model__max_depth": [None, 4, 6, 8, 12, 16, 20],
            "model__min_samples_split": randint(2, 20),
            "model__min_samples_leaf": randint(1, 10),
            "model__max_features": ["sqrt", "log2", None],
            "model__class_weight": ["balanced", "balanced_subsample"],
        },
    )

    xgb = Pipeline([
        ("preprocess", make_preprocessor(numeric, categorical, False)),
        ("model", XGBClassifier(
            objective="binary:logistic",
            eval_metric="logloss",
            tree_method="hist",
            random_state=seed,
            n_jobs=1,
            verbosity=0,
        )),
    ])
    searches["xgboost"] = (
        xgb,
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
        for name, (pipeline, params) in searches.items()
    }


def choose_threshold(y_true, probabilities, recall_floor):
    # Threshold is selected using training-fold OOF predictions only.
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

    eligible = [r for r in rows if r["recall"] >= recall_floor]
    if eligible:
        # Prefer the highest F1; break ties toward the higher threshold.
        return max(eligible, key=lambda r: (r["f1"], r["threshold"]))
    # If the recall floor cannot be met, report the best-recall threshold.
    return max(rows, key=lambda r: (r["recall"], r["f1"], r["threshold"]))


def main():
    started = time.time()
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

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

    print(f"Rows: {len(X)} | Features: {X.shape[1]}")
    print(
        f"Nested CV smoke test: {OUTER_FOLDS} outer folds, "
        f"{INNER_FOLDS} inner folds, {N_ITER} configs/model"
    )
    print("No existing model artifacts or reports will be overwritten.")

    for fold, (train_idx, test_idx) in enumerate(outer_cv.split(X, y), start=1):
        print(f"\nOuter fold {fold}/{OUTER_FOLDS}")
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

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
            print(f"  Tuning {name}...")
            search.fit(X_train, y_train)
            fitted[name] = search
            print(f"    Inner-CV average precision: {search.best_score_:.4f}")

        # Model selection occurs using inner-CV average precision only.
        selected_name, selected_search = max(
            fitted.items(), key=lambda item: item[1].best_score_
        )
        selected_models.append(selected_name)
        print(f"  Selected model: {selected_name}")

        # Generate OOF probabilities within the outer training fold to select
        # a threshold. The outer test fold is not passed to this procedure.
        from sklearn.base import clone
        from sklearn.model_selection import cross_val_predict

        threshold_cv = StratifiedKFold(
            n_splits=INNER_FOLDS,
            shuffle=True,
            random_state=RANDOM_STATE + 100 + fold,
        )
        oof_probabilities = cross_val_predict(
            clone(selected_search.best_estimator_),
            X_train,
            y_train,
            cv=threshold_cv,
            method="predict_proba",
            n_jobs=1,
        )[:, 1]
        threshold_info = choose_threshold(
            y_train.to_numpy(), oof_probabilities, RECALL_FLOOR
        )
        threshold = threshold_info["threshold"]

        # The selected estimator was refitted on all outer training rows by
        # RandomizedSearchCV(refit=True); test data is used only here.
        test_probabilities = selected_search.best_estimator_.predict_proba(X_test)[:, 1]
        test_predictions = (test_probabilities >= threshold).astype(int)

        row = {
            "outer_fold": fold,
            "selected_model": selected_name,
            "inner_cv_average_precision": float(selected_search.best_score_),
            "selected_threshold": float(threshold),
            "threshold_training_oof_recall": float(threshold_info["recall"]),
            "threshold_training_oof_precision": float(threshold_info["precision"]),
            "threshold_training_oof_f1": float(threshold_info["f1"]),
            "test_accuracy": float(accuracy_score(y_test, test_predictions)),
            "test_precision": float(precision_score(y_test, test_predictions, zero_division=0)),
            "test_recall": float(recall_score(y_test, test_predictions, zero_division=0)),
            "test_f1": float(f1_score(y_test, test_predictions, zero_division=0)),
            "test_roc_auc": float(roc_auc_score(y_test, test_probabilities)),
            "test_average_precision": float(average_precision_score(y_test, test_probabilities)),
            "test_rows": int(len(test_idx)),
        }
        results.append(row)
        print(
            f"  Test AP={row['test_average_precision']:.4f}, "
            f"F1={row['test_f1']:.4f}, recall={row['test_recall']:.4f}, "
            f"threshold={threshold:.3f}"
        )

    results_df = pd.DataFrame(results)
    metrics_path = REPORT_DIR / "nested_cv_fold_metrics_v1.csv"
    summary_path = REPORT_DIR / "nested_cv_evaluation_v1.json"

    # Refuse to overwrite prior output from an earlier run.
    if metrics_path.exists() or summary_path.exists():
        raise FileExistsError(
            "Nested-CV output already exists. Rename or archive these new "
            "outputs before running again; no files were written."
        )

    results_df.to_csv(metrics_path, index=False)
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
        "method": "Nested stratified cross-validation",
        "outer_folds": OUTER_FOLDS,
        "inner_folds": INNER_FOLDS,
        "randomized_configurations_per_model_per_outer_fold": N_ITER,
        "primary_inner_selection_metric": "average_precision",
        "threshold_selection": (
            "Training-fold out-of-fold probabilities; maximize F1 among "
            "thresholds meeting recall >= 0.80, with higher threshold as tie-break"
        ),
        "outer_test_fold_used_for_model_or_threshold_selection": False,
        "outer_fold_selected_models": selected_models,
        "mean_outer_test_metrics": {
            col: float(results_df[col].mean()) for col in metric_columns
        },
        "std_outer_test_metrics": {
            col: float(results_df[col].std(ddof=1)) for col in metric_columns
        },
        "interpretation_warning": (
            "Initial smoke-test configuration, not the final full evaluation. "
            "These are nested-CV estimates, not results from a newly untouched "
            "holdout. The historical holdout has already influenced earlier "
            "model/threshold choices."
        ),
        "elapsed_seconds": round(time.time() - started, 2),
    }
    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\nSmoke-test evaluation completed.")
    print(f"Fold metrics: {metrics_path}")
    print(f"Summary: {summary_path}")
    print("\nMean outer-test metrics:")
    print(results_df[metric_columns].mean().to_string())


if __name__ == "__main__":
    main()
