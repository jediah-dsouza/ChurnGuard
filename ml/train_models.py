"""
ChurnGuard — Candidate Model Training & Tuning

Stage:
    Leakage-safe candidate-model training

Models:
    1. Majority-class baseline
    2. Logistic Regression
    3. Random Forest
    4. XGBoost

Design:
    - Reconstructs the exact deterministic train/holdout split used by
      prepare_data.py.
    - Keeps the untouched holdout completely outside model tuning.
    - Performs all preprocessing inside sklearn Pipelines.
    - Uses 5-fold Stratified CV.
    - Uses RandomizedSearchCV for candidate tuning.
    - Uses Average Precision / PR-AUC as the primary tuning metric.
    - Reports ROC-AUC, PR-AUC, recall, precision, F1 and accuracy.
    - Saves tuned candidate pipelines with joblib.
    - Writes reproducible JSON reports.

IMPORTANT:
    The holdout is NOT used for hyperparameter tuning, feature selection,
    preprocessing fitting, threshold selection, or model selection.
"""

from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from scipy.stats import randint, uniform
from sklearn.compose import ColumnTransformer
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
from sklearn.model_selection import (
    RandomizedSearchCV,
    StratifiedKFold,
    train_test_split,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier


# ============================================================================
# PROJECT PATHS
# ============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ML_DIR = PROJECT_ROOT / "ml"

DATA_PATH = (
    ML_DIR
    / "data"
    / "WA_Fn-UseC_-Telco-Customer-Churn.csv"
)

REPORTS_DIR = ML_DIR / "reports"
MODELS_DIR = ML_DIR / "models"

REPORTS_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================================
# EXPERIMENT CONFIGURATION
# ============================================================================

RANDOM_STATE = 42
HOLDOUT_SIZE = 0.20
CV_FOLDS = 5

# Number of random parameter configurations tested per candidate.
# 10 gives a meaningful search while keeping the internship workflow
# practical on a normal laptop.
N_ITER = 10

PRIMARY_SCORING = "average_precision"

TARGET_COLUMN = "Churn"
ID_COLUMN = "customerID"

POSITIVE_LABEL = "Yes"
NEGATIVE_LABEL = "No"

EXPECTED_TOTAL_ROWS = 7043
EXPECTED_HOLDOUT_ROWS = 1409
EXPECTED_TRAIN_ROWS = 5634

EXPECTED_FEATURE_COUNT = 19


# ============================================================================
# HELPERS
# ============================================================================


def utc_timestamp() -> str:
    """Return an ISO-8601 UTC timestamp."""
    return datetime.now(timezone.utc).isoformat()


def json_safe(value: Any) -> Any:
    """Convert numpy/scikit-learn values into JSON-safe Python values."""
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}

    if isinstance(value, (list, tuple)):
        return [json_safe(v) for v in value]

    if isinstance(value, np.ndarray):
        return value.tolist()

    if isinstance(value, (np.integer,)):
        return int(value)

    if isinstance(value, (np.floating,)):
        return float(value)

    if isinstance(value, np.bool_):
        return bool(value)

    if pd.isna(value):
        return None

    return value


def print_header(title: str) -> None:
    print()
    print("=" * 72)
    print(title)
    print("=" * 72)


def make_one_hot_encoder() -> OneHotEncoder:
    """
    Build an encoder compatible with current sklearn versions.

    sparse_output=True keeps the transformed feature matrix efficient.
    """
    return OneHotEncoder(
        handle_unknown="ignore",
        sparse_output=True,
    )


# ============================================================================
# DATA LOADING & VALIDATION
# ============================================================================


def load_and_validate_dataset() -> pd.DataFrame:
    print_header("[1/8] Loading and validating dataset...")

    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found:\n{DATA_PATH}"
        )

    df = pd.read_csv(DATA_PATH)

    print(f"Dataset: {DATA_PATH}")
    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns):,}")

    if len(df) != EXPECTED_TOTAL_ROWS:
        raise ValueError(
            f"Unexpected row count: {len(df)}. "
            f"Expected {EXPECTED_TOTAL_ROWS}."
        )

    required_columns = {
        ID_COLUMN,
        TARGET_COLUMN,
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
    }

    missing_columns = sorted(required_columns - set(df.columns))

    if missing_columns:
        raise ValueError(
            "Required columns are missing:\n"
            + "\n".join(f"  - {column}" for column in missing_columns)
        )

    duplicate_ids = int(df[ID_COLUMN].duplicated().sum())

    if duplicate_ids != 0:
        raise ValueError(
            f"Duplicate customer IDs detected: {duplicate_ids}"
        )

    if df[ID_COLUMN].isna().any():
        raise ValueError("Missing customer IDs detected.")

    if df[TARGET_COLUMN].isna().any():
        raise ValueError("Missing target values detected.")

    target_values = set(df[TARGET_COLUMN].astype(str).unique())

    if target_values != {NEGATIVE_LABEL, POSITIVE_LABEL}:
        raise ValueError(
            f"Unexpected target values: {sorted(target_values)}"
        )

    # These are the known leakage-sensitive columns from the previous
    # leakage-capstone work. They must never be present in this clean
    # training dataset.
    forbidden_leakage_columns = {
        "churn_risk_score",
        "post_outcome_churn_flag",
    }

    found_leakage_columns = sorted(
        forbidden_leakage_columns.intersection(df.columns)
    )

    if found_leakage_columns:
        raise ValueError(
            "Known target-derived/post-outcome leakage columns detected:\n"
            + "\n".join(f"  - {column}" for column in found_leakage_columns)
        )

    # TotalCharges contains 11 blank values in the original Telco dataset.
    # Keep them here. Imputation happens INSIDE the sklearn preprocessing
    # pipeline and therefore is fitted only on each training fold.
    df["TotalCharges"] = pd.to_numeric(
        df["TotalCharges"],
        errors="coerce",
    )

    print("Dataset validation: PASS")
    print(f"Duplicate customer IDs: {duplicate_ids}")
    print(
        "Known target-derived/post-outcome leakage columns: NONE"
    )
    print(
        "TotalCharges missing after numeric conversion: "
        f"{int(df['TotalCharges'].isna().sum())}"
    )

    return df


# ============================================================================
# FEATURE DEFINITION
# ============================================================================


def define_features(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.Series, list[str], list[str], list[str]]:
    print_header("[2/8] Defining leakage-safe model features...")

    excluded_columns = {
        ID_COLUMN,
        TARGET_COLUMN,
    }

    feature_columns = [
        column
        for column in df.columns
        if column not in excluded_columns
    ]

    if len(feature_columns) != EXPECTED_FEATURE_COUNT:
        raise ValueError(
            f"Expected {EXPECTED_FEATURE_COUNT} model features, "
            f"found {len(feature_columns)}."
        )

    X = df[feature_columns].copy()

    # Binary target:
    # No -> 0
    # Yes -> 1
    y = (
        df[TARGET_COLUMN]
        .map(
            {
                NEGATIVE_LABEL: 0,
                POSITIVE_LABEL: 1,
            }
        )
        .astype(int)
    )

    numeric_features = [
        "tenure",
        "MonthlyCharges",
        "TotalCharges",
    ]

    categorical_features = [
        column
        for column in feature_columns
        if column not in numeric_features
    ]

    if len(numeric_features) + len(categorical_features) != len(
        feature_columns
    ):
        raise AssertionError(
            "Numeric and categorical feature definitions do not cover "
            "all model features."
        )

    print(f"Model features: {len(feature_columns)}")
    print(f"Numeric features: {len(numeric_features)}")
    print(f"Categorical features: {len(categorical_features)}")
    print("customerID excluded: YES")
    print("Churn excluded: YES")

    return (
        X,
        y,
        feature_columns,
        numeric_features,
        categorical_features,
    )


# ============================================================================
# DETERMINISTIC TRAIN / HOLDOUT SPLIT
# ============================================================================


def create_locked_split(
    df: pd.DataFrame,
    X: pd.DataFrame,
    y: pd.Series,
) -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.Series,
    pd.Series,
    pd.DataFrame,
    pd.DataFrame,
]:
    print_header("[3/8] Reconstructing and locking train/holdout split...")

    (
        X_train,
        X_holdout,
        y_train,
        y_holdout,
        ids_train,
        ids_holdout,
    ) = train_test_split(
        X,
        y,
        df[[ID_COLUMN]],
        test_size=HOLDOUT_SIZE,
        stratify=y,
        random_state=RANDOM_STATE,
    )

    if len(X_train) != EXPECTED_TRAIN_ROWS:
        raise AssertionError(
            f"Unexpected training rows: {len(X_train)}. "
            f"Expected {EXPECTED_TRAIN_ROWS}."
        )

    if len(X_holdout) != EXPECTED_HOLDOUT_ROWS:
        raise AssertionError(
            f"Unexpected holdout rows: {len(X_holdout)}. "
            f"Expected {EXPECTED_HOLDOUT_ROWS}."
        )

    train_ids = set(ids_train[ID_COLUMN])
    holdout_ids = set(ids_holdout[ID_COLUMN])

    overlap = train_ids.intersection(holdout_ids)

    if overlap:
        raise AssertionError(
            f"Train/holdout customer ID overlap detected: "
            f"{len(overlap)}"
        )

    overall_rate = float(y.mean())
    train_rate = float(y_train.mean())
    holdout_rate = float(y_holdout.mean())

    print(f"Training rows: {len(X_train):,}")
    print(f"Untouched holdout rows: {len(X_holdout):,}")
    print(f"Overall churn rate: {overall_rate:.4%}")
    print(f"Training churn rate: {train_rate:.4%}")
    print(f"Holdout churn rate: {holdout_rate:.4%}")
    print("Customer ID overlap: 0")

    # Save the exact split manifest. IDs are stored only as split metadata;
    # they are NOT model features.
    split_manifest = {
        "created_at_utc": utc_timestamp(),
        "random_state": RANDOM_STATE,
        "holdout_size": HOLDOUT_SIZE,
        "total_rows": len(df),
        "training_rows": len(X_train),
        "holdout_rows": len(X_holdout),
        "overall_churn_rate": overall_rate,
        "training_churn_rate": train_rate,
        "holdout_churn_rate": holdout_rate,
        "train_customer_ids": sorted(train_ids),
        "holdout_customer_ids": sorted(holdout_ids),
    }

    split_manifest_path = REPORTS_DIR / "split_manifest.json"

    with split_manifest_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            split_manifest,
            file,
            indent=2,
        )

    print(f"Split manifest written to: {split_manifest_path}")

    return (
        X_train,
        X_holdout,
        y_train,
        y_holdout,
        ids_train,
        ids_holdout,
    )


# ============================================================================
# PREPROCESSING
# ============================================================================


def build_preprocessor(
    numeric_features: list[str],
    categorical_features: list[str],
    scale_numeric: bool,
) -> ColumnTransformer:
    """
    Build leakage-safe preprocessing.

    Numeric:
        median imputation
        optional standardization

    Categorical:
        most-frequent imputation
        one-hot encoding

    Because this transformer lives inside each model Pipeline, it is fitted
    separately inside every CV training fold.
    """

    if scale_numeric:
        numeric_pipeline = Pipeline(
            steps=[
                (
                    "imputer",
                    SimpleImputer(strategy="median"),
                ),
                (
                    "scaler",
                    StandardScaler(),
                ),
            ]
        )
    else:
        numeric_pipeline = Pipeline(
            steps=[
                (
                    "imputer",
                    SimpleImputer(strategy="median"),
                ),
            ]
        )

    categorical_pipeline = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(strategy="most_frequent"),
            ),
            (
                "onehot",
                make_one_hot_encoder(),
            ),
        ]
    )

    return ColumnTransformer(
        transformers=[
            (
                "numeric",
                numeric_pipeline,
                numeric_features,
            ),
            (
                "categorical",
                categorical_pipeline,
                categorical_features,
            ),
        ],
        remainder="drop",
    )


# ============================================================================
# MODEL DEFINITIONS
# ============================================================================


def build_model_searches(
    numeric_features: list[str],
    categorical_features: list[str],
) -> dict[str, RandomizedSearchCV]:
    print_header("[4/8] Building candidate model pipelines...")

    cv = StratifiedKFold(
        n_splits=CV_FOLDS,
        shuffle=True,
        random_state=RANDOM_STATE,
    )

    searches: dict[str, RandomizedSearchCV] = {}

    # ------------------------------------------------------------------------
    # Logistic Regression
    # ------------------------------------------------------------------------

    logistic_preprocessor = build_preprocessor(
        numeric_features=numeric_features,
        categorical_features=categorical_features,
        scale_numeric=True,
    )

    logistic_pipeline = Pipeline(
        steps=[
            (
                "preprocess",
                logistic_preprocessor,
            ),
            (
                "model",
                LogisticRegression(
                    class_weight="balanced",
                    solver="liblinear",
                    max_iter=2000,
                    random_state=RANDOM_STATE,
                ),
            ),
        ]
    )

    logistic_params = {
        "model__C": uniform(0.01, 10.0),
        "model__penalty": ["l1", "l2"],
    }

    searches["logistic_regression"] = RandomizedSearchCV(
        estimator=logistic_pipeline,
        param_distributions=logistic_params,
        n_iter=N_ITER,
        scoring=PRIMARY_SCORING,
        cv=cv,
        refit=True,
        random_state=RANDOM_STATE,
        n_jobs=-1,
        verbose=1,
        return_train_score=False,
    )

    # ------------------------------------------------------------------------
    # Random Forest
    # ------------------------------------------------------------------------

    rf_preprocessor = build_preprocessor(
        numeric_features=numeric_features,
        categorical_features=categorical_features,
        scale_numeric=False,
    )

    rf_pipeline = Pipeline(
        steps=[
            (
                "preprocess",
                rf_preprocessor,
            ),
            (
                "model",
                RandomForestClassifier(
                    class_weight="balanced_subsample",
                    random_state=RANDOM_STATE,
                    n_jobs=-1,
                ),
            ),
        ]
    )

    rf_params = {
        "model__n_estimators": randint(200, 700),
        "model__max_depth": [None, 4, 6, 8, 12, 16, 20],
        "model__min_samples_split": randint(2, 20),
        "model__min_samples_leaf": randint(1, 10),
        "model__max_features": [
            "sqrt",
            "log2",
            None,
        ],
        "model__class_weight": [
            "balanced",
            "balanced_subsample",
        ],
    }

    searches["random_forest"] = RandomizedSearchCV(
        estimator=rf_pipeline,
        param_distributions=rf_params,
        n_iter=N_ITER,
        scoring=PRIMARY_SCORING,
        cv=cv,
        refit=True,
        random_state=RANDOM_STATE,
        n_jobs=-1,
        verbose=1,
        return_train_score=False,
    )

    # ------------------------------------------------------------------------
    # XGBoost
    # ------------------------------------------------------------------------

    xgb_preprocessor = build_preprocessor(
        numeric_features=numeric_features,
        categorical_features=categorical_features,
        scale_numeric=False,
    )

    # Training data churn prevalence is approximately 26.5%.
    # scale_pos_weight therefore starts around:
    # negative / positive ≈ 73.5 / 26.5 ≈ 2.77
    #
    # We allow RandomizedSearchCV to tune it around this sensible range.
    xgb_pipeline = Pipeline(
        steps=[
            (
                "preprocess",
                xgb_preprocessor,
            ),
            (
                "model",
                XGBClassifier(
                    objective="binary:logistic",
                    eval_metric="logloss",
                    tree_method="hist",
                    random_state=RANDOM_STATE,
                    n_jobs=-1,
                    verbosity=0,
                ),
            ),
        ]
    )

    xgb_params = {
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
    }

    searches["xgboost"] = RandomizedSearchCV(
        estimator=xgb_pipeline,
        param_distributions=xgb_params,
        n_iter=N_ITER,
        scoring=PRIMARY_SCORING,
        cv=cv,
        refit=True,
        random_state=RANDOM_STATE,
        n_jobs=-1,
        verbose=1,
        return_train_score=False,
    )

    print("Candidate pipelines created:")
    print("  - Logistic Regression")
    print("  - Random Forest")
    print("  - XGBoost")
    print()
    print(f"Primary tuning metric: {PRIMARY_SCORING}")
    print(f"Stratified CV folds: {CV_FOLDS}")
    print(f"Randomized configurations per model: {N_ITER}")

    return searches


# ============================================================================
# BASELINE
# ============================================================================


def calculate_majority_baseline(
    y_train: pd.Series,
    y_holdout: pd.Series,
) -> dict[str, Any]:
    print_header("[5/8] Calculating majority-class baseline...")

    majority_class = int(y_train.mode()[0])

    predictions = np.full(
        shape=len(y_holdout),
        fill_value=majority_class,
        dtype=int,
    )

    accuracy = accuracy_score(
        y_holdout,
        predictions,
    )

    precision = precision_score(
        y_holdout,
        predictions,
        zero_division=0,
    )

    recall = recall_score(
        y_holdout,
        predictions,
        zero_division=0,
    )

    f1 = f1_score(
        y_holdout,
        predictions,
        zero_division=0,
    )

    result = {
        "model": "majority_baseline",
        "tuning_metric": None,
        "cv_best_score": None,
        "holdout_accuracy": float(accuracy),
        "holdout_precision": float(precision),
        "holdout_recall": float(recall),
        "holdout_f1": float(f1),
        "holdout_roc_auc": None,
        "holdout_pr_auc": None,
        "majority_class": (
            POSITIVE_LABEL
            if majority_class == 1
            else NEGATIVE_LABEL
        ),
    }

    print(
        f"Majority class: {result['majority_class']}"
    )
    print(
        f"Holdout accuracy: {accuracy:.4%}"
    )
    print(
        f"Holdout churn recall: {recall:.4%}"
    )

    return result


# ============================================================================
# SEARCH / EVALUATION
# ============================================================================


def evaluate_probability_model(
    model_name: str,
    fitted_search: RandomizedSearchCV,
    X_holdout: pd.DataFrame,
    y_holdout: pd.Series,
) -> dict[str, Any]:
    """
    Evaluate the tuned model on the untouched holdout.

    IMPORTANT:
        This is descriptive evaluation only.

        The holdout results must NOT be used to tune the model or select
        the production threshold. That happens in the next ML stage.
    """

    best_estimator = fitted_search.best_estimator_

    probabilities = best_estimator.predict_proba(
        X_holdout
    )[:, 1]

    predictions = (
        probabilities >= 0.50
    ).astype(int)

    accuracy = accuracy_score(
        y_holdout,
        predictions,
    )

    precision = precision_score(
        y_holdout,
        predictions,
        zero_division=0,
    )

    recall = recall_score(
        y_holdout,
        predictions,
        zero_division=0,
    )

    f1 = f1_score(
        y_holdout,
        predictions,
        zero_division=0,
    )

    roc_auc = roc_auc_score(
        y_holdout,
        probabilities,
    )

    pr_auc = average_precision_score(
        y_holdout,
        probabilities,
    )

    return {
        "model": model_name,
        "tuning_metric": PRIMARY_SCORING,
        "cv_best_score": float(
            fitted_search.best_score_
        ),
        "holdout_accuracy": float(accuracy),
        "holdout_precision": float(precision),
        "holdout_recall": float(recall),
        "holdout_f1": float(f1),
        "holdout_roc_auc": float(roc_auc),
        "holdout_pr_auc": float(pr_auc),
        "default_probability_threshold": 0.50,
        "best_params": json_safe(
            fitted_search.best_params_
        ),
        "search_iterations": N_ITER,
        "cv_folds": CV_FOLDS,
    }


def train_candidate_models(
    searches: dict[str, RandomizedSearchCV],
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_holdout: pd.DataFrame,
    y_holdout: pd.Series,
) -> tuple[list[dict[str, Any]], dict[str, RandomizedSearchCV]]:
    print_header("[6/8] Running 5-fold Stratified RandomizedSearchCV...")

    results: list[dict[str, Any]] = []

    total_models = len(searches)

    for index, (model_name, search) in enumerate(
        searches.items(),
        start=1,
    ):
        print()
        print("-" * 72)
        print(
            f"MODEL {index}/{total_models}: "
            f"{model_name}"
        )
        print("-" * 72)

        started = time.perf_counter()

        search.fit(
            X_train,
            y_train,
        )

        elapsed = time.perf_counter() - started

        print()
        print(
            f"{model_name} tuning complete "
            f"in {elapsed:.2f} seconds."
        )

        print(
            f"Best CV PR-AUC: "
            f"{search.best_score_:.6f}"
        )

        print("Best parameters:")

        for key, value in search.best_params_.items():
            print(f"  {key}: {value}")

        result = evaluate_probability_model(
            model_name=model_name,
            fitted_search=search,
            X_holdout=X_holdout,
            y_holdout=y_holdout,
        )

        result["training_seconds"] = round(
            elapsed,
            3,
        )

        results.append(result)

        print()
        print("Untouched holdout — descriptive evaluation:")
        print(
            f"  Accuracy : {result['holdout_accuracy']:.4f}"
        )
        print(
            f"  Precision: {result['holdout_precision']:.4f}"
        )
        print(
            f"  Recall   : {result['holdout_recall']:.4f}"
        )
        print(
            f"  F1       : {result['holdout_f1']:.4f}"
        )
        print(
            f"  ROC-AUC  : {result['holdout_roc_auc']:.4f}"
        )
        print(
            f"  PR-AUC   : {result['holdout_pr_auc']:.4f}"
        )

    return results, searches


# ============================================================================
# SERIALIZATION
# ============================================================================


def save_candidate_models(
    searches: dict[str, RandomizedSearchCV],
) -> dict[str, str]:
    print_header("[7/8] Saving tuned candidate pipelines...")

    saved_paths: dict[str, str] = {}

    for model_name, search in searches.items():
        model_path = MODELS_DIR / (
            f"{model_name}_tuned_cv_v1.joblib"
        )

        joblib.dump(
            search.best_estimator_,
            model_path,
        )

        saved_paths[model_name] = str(model_path)

        print(
            f"{model_name}: {model_path}"
        )

    return saved_paths


# ============================================================================
# REPORTING
# ============================================================================


def write_training_report(
    feature_columns: list[str],
    numeric_features: list[str],
    categorical_features: list[str],
    y_train: pd.Series,
    y_holdout: pd.Series,
    baseline_result: dict[str, Any],
    model_results: list[dict[str, Any]],
    saved_paths: dict[str, str],
) -> Path:
    print_header("[8/8] Writing training report...")

    all_results = [
        baseline_result,
        *model_results,
    ]

    # Candidate selection is based on CV PR-AUC, not holdout performance.
    ranked_candidates = sorted(
        model_results,
        key=lambda item: item["cv_best_score"],
        reverse=True,
    )

    recommended_candidate = (
        ranked_candidates[0]["model"]
        if ranked_candidates
        else None
    )

    report = {
        "experiment": {
            "name": "churnguard_candidate_model_training",
            "version": "v1",
            "created_at_utc": utc_timestamp(),
            "random_state": RANDOM_STATE,
            "primary_tuning_metric": PRIMARY_SCORING,
            "cv_folds": CV_FOLDS,
            "randomized_search_iterations": N_ITER,
        },
        "dataset": {
            "path": str(DATA_PATH),
            "rows": EXPECTED_TOTAL_ROWS,
            "target_column": TARGET_COLUMN,
            "identifier_column": ID_COLUMN,
            "positive_class": POSITIVE_LABEL,
            "negative_class": NEGATIVE_LABEL,
        },
        "split": {
            "training_rows": len(y_train),
            "holdout_rows": len(y_holdout),
            "training_churn_rate": float(y_train.mean()),
            "holdout_churn_rate": float(y_holdout.mean()),
            "holdout_locked": True,
            "split_manifest": str(
                REPORTS_DIR / "split_manifest.json"
            ),
        },
        "features": {
            "count": len(feature_columns),
            "columns": feature_columns,
            "numeric": numeric_features,
            "categorical": categorical_features,
            "identifier_excluded": True,
            "target_excluded": True,
        },
        "models": all_results,
        "candidate_ranking_by_cv_pr_auc": [
            {
                "rank": rank,
                "model": result["model"],
                "cv_pr_auc": result["cv_best_score"],
            }
            for rank, result in enumerate(
                ranked_candidates,
                start=1,
            )
        ],
        "recommended_candidate_for_next_stage": (
            recommended_candidate
        ),
        "model_artifacts": saved_paths,
        "important_evaluation_note": (
            "Holdout metrics are descriptive only at this stage. "
            "The holdout must not be used for hyperparameter tuning, "
            "feature selection, model selection, or business threshold "
            "optimization. The next stage will perform formal untouched "
            "holdout evaluation and business threshold analysis."
        ),
    }

    report_path = (
        REPORTS_DIR
        / "candidate_model_training_report.json"
    )

    with report_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            json_safe(report),
            file,
            indent=2,
        )

    print(f"Training report: {report_path}")

    print()
    print("Candidate ranking by CV PR-AUC:")

    for rank, result in enumerate(
        ranked_candidates,
        start=1,
    ):
        print(
            f"  {rank}. "
            f"{result['model']} — "
            f"CV PR-AUC "
            f"{result['cv_best_score']:.6f}"
        )

    print()
    print(
        f"Recommended candidate for next stage: "
        f"{recommended_candidate}"
    )

    return report_path


# ============================================================================
# MAIN
# ============================================================================


def main() -> int:
    started = time.perf_counter()

    print_header(
        "ChurnGuard — Candidate Model Training & Tuning"
    )

    print("Primary metric: Average Precision / PR-AUC")
    print("CV strategy: 5-fold StratifiedKFold")
    print("Hyperparameter search: RandomizedSearchCV")
    print("Random state:", RANDOM_STATE)
    print()
    print(
        "IMPORTANT: The untouched holdout will NOT be used "
        "for tuning."
    )

    try:
        # --------------------------------------------------------------
        # 1. Load / validate
        # --------------------------------------------------------------
        df = load_and_validate_dataset()

        # --------------------------------------------------------------
        # 2. Features
        # --------------------------------------------------------------
        (
            X,
            y,
            feature_columns,
            numeric_features,
            categorical_features,
        ) = define_features(df)

        # --------------------------------------------------------------
        # 3. Exact deterministic split
        # --------------------------------------------------------------
        (
            X_train,
            X_holdout,
            y_train,
            y_holdout,
            _ids_train,
            _ids_holdout,
        ) = create_locked_split(
            df=df,
            X=X,
            y=y,
        )

        # --------------------------------------------------------------
        # 4. Build model searches
        # --------------------------------------------------------------
        searches = build_model_searches(
            numeric_features=numeric_features,
            categorical_features=categorical_features,
        )

        # --------------------------------------------------------------
        # 5. Majority baseline
        # --------------------------------------------------------------
        baseline_result = calculate_majority_baseline(
            y_train=y_train,
            y_holdout=y_holdout,
        )

        # --------------------------------------------------------------
        # 6. Train / tune candidate models
        # --------------------------------------------------------------
        model_results, fitted_searches = train_candidate_models(
            searches=searches,
            X_train=X_train,
            y_train=y_train,
            X_holdout=X_holdout,
            y_holdout=y_holdout,
        )

        # --------------------------------------------------------------
        # 7. Save fitted candidate pipelines
        # --------------------------------------------------------------
        saved_paths = save_candidate_models(
            searches=fitted_searches,
        )

        # --------------------------------------------------------------
        # 8. Report
        # --------------------------------------------------------------
        report_path = write_training_report(
            feature_columns=feature_columns,
            numeric_features=numeric_features,
            categorical_features=categorical_features,
            y_train=y_train,
            y_holdout=y_holdout,
            baseline_result=baseline_result,
            model_results=model_results,
            saved_paths=saved_paths,
        )

        elapsed = time.perf_counter() - started

        print()
        print("=" * 72)
        print("CANDIDATE MODEL TRAINING STAGE PASSED")
        print("=" * 72)
        print(
            f"Total runtime: {elapsed:.2f} seconds"
        )
        print()
        print("Artifacts:")
        print(f"  {report_path}")
        print(f"  {REPORTS_DIR / 'split_manifest.json'}")

        for path in saved_paths.values():
            print(f"  {path}")

        print()
        print(
            "Holdout status: LOCKED / descriptive evaluation only"
        )
        print(
            "Next stage: formal holdout evaluation + "
            "business threshold analysis"
        )

        return 0

    except KeyboardInterrupt:
        print()
        print("Training interrupted by user.")
        return 130

    except Exception as exc:
        print()
        print("=" * 72)
        print("CANDIDATE MODEL TRAINING STAGE FAILED")
        print("=" * 72)
        print(f"{type(exc).__name__}: {exc}")
        print()
        print(
            "No stage PASS should be recorded until the failure "
            "has been resolved and the complete script rerun."
        )

        return 1


if __name__ == "__main__":
    sys.exit(main())