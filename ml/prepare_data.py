"""
ChurnGuard — Leakage-Safe Data Preparation

Purpose
-------
Validate the approved Telco Customer Churn dataset and establish the
reproducible train/holdout foundation for the ChurnGuard ML pipeline.

This stage does NOT train a model.

The script:

1. Loads the approved original Telco Customer Churn dataset.
2. Validates the expected schema.
3. Validates customer IDs.
4. Validates the Churn target.
5. Checks for known target-derived/post-outcome leakage columns.
6. Converts TotalCharges to numeric.
7. Preserves legitimate missing TotalCharges values for later
   pipeline-level imputation.
8. Excludes customerID from model features.
9. Excludes Churn from model features.
10. Creates a reproducible stratified 80/20 train/holdout split.
11. Calculates the majority-class baseline on the untouched holdout.
12. Writes a JSON preparation report.

Important leakage rules
-----------------------
customerID:
    Allowed in the raw dataset.
    NEVER used as a model feature.

Churn:
    The prediction target.
    NEVER used as a model feature.

churn_risk_score:
    Forbidden target-derived feature.

post_outcome_churn_flag:
    Forbidden post-outcome feature.

TotalCharges:
    Converted to numeric here.
    Missing values are NOT filled here.
    Imputation will happen inside the ML preprocessing pipeline,
    fitted on training data only.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split


# ============================================================================
# Configuration
# ============================================================================

RANDOM_STATE = 42
TEST_SIZE = 0.20

TARGET_COLUMN = "Churn"
ID_COLUMN = "customerID"

EXPECTED_TARGET_VALUES = {
    "No",
    "Yes",
}

# These are genuinely forbidden because they contain information derived
# from the target or information that would only be available after the
# churn outcome.
FORBIDDEN_LEAKAGE_COLUMNS = {
    "churn_risk_score",
    "post_outcome_churn_flag",
}


# ============================================================================
# Paths
# ============================================================================

# __file__:
#   ChurnGuard/ml/prepare_data.py
#
# parents[0]:
#   ChurnGuard/ml
#
# parents[1]:
#   ChurnGuard
PROJECT_ROOT = Path(__file__).resolve().parents[1]

ML_DIR = PROJECT_ROOT / "ml"

DATA_PATH = (
    ML_DIR
    / "data"
    / "WA_Fn-UseC_-Telco-Customer-Churn.csv"
)

REPORTS_DIR = ML_DIR / "reports"

REPORT_PATH = (
    REPORTS_DIR
    / "data_preparation_report.json"
)


# ============================================================================
# Helpers
# ============================================================================

def fail(message: str) -> None:
    """Stop execution with a clear validation error."""
    raise ValueError(message)


# ============================================================================
# Main
# ============================================================================

def main() -> None:
    print("=" * 72)
    print("ChurnGuard — Leakage-Safe Data Preparation")
    print("=" * 72)

    # ========================================================================
    # 1. Load dataset
    # ========================================================================

    print("\n[1/9] Loading dataset...")

    if not DATA_PATH.exists():
        fail(
            "Dataset not found:\n"
            f"{DATA_PATH}"
        )

    df = pd.read_csv(DATA_PATH)

    print(f"Dataset: {DATA_PATH}")
    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")

    # ========================================================================
    # 2. Validate required columns
    # ========================================================================

    print("\n[2/9] Validating required columns...")

    required_columns = {
        ID_COLUMN,
        TARGET_COLUMN,
    }

    missing_required_columns = sorted(
        required_columns - set(df.columns)
    )

    if missing_required_columns:
        fail(
            "Required columns are missing from the approved dataset: "
            f"{missing_required_columns}"
        )

    print(f"Target column: {TARGET_COLUMN}")
    print(f"Identifier column: {ID_COLUMN}")

    # ========================================================================
    # 3. Validate basic dataset structure
    # ========================================================================

    print("\n[3/9] Validating dataset structure...")

    if df.empty:
        fail("The approved dataset contains zero rows.")

    if df.columns.duplicated().any():
        duplicated_columns = sorted(
            df.columns[df.columns.duplicated()].tolist()
        )

        fail(
            "Duplicate column names detected: "
            f"{duplicated_columns}"
        )

    print("Dataset structure: PASS")

    # ========================================================================
    # 4. Check known leakage columns
    # ========================================================================

    print("\n[4/9] Checking for known leakage columns...")

    # IMPORTANT:
    #
    # customerID is intentionally NOT included in this set.
    #
    # customerID is a raw identifier. It is allowed to exist in the source
    # dataset but is explicitly removed from model features later.
    #
    # Only target-derived/post-outcome columns are rejected here.

    leakage_columns_present = sorted(
        FORBIDDEN_LEAKAGE_COLUMNS.intersection(
            df.columns
        )
    )

    if leakage_columns_present:
        fail(
            "Leakage-sensitive columns detected in the approved dataset: "
            f"{leakage_columns_present}"
        )

    print(
        "Known target-derived/post-outcome leakage columns: NONE"
    )

    # ========================================================================
    # 5. Validate identifiers and target
    # ========================================================================

    print("\n[5/9] Validating identifiers and target...")

    # ------------------------------------------------------------------------
    # Customer IDs
    # ------------------------------------------------------------------------

    duplicate_customer_ids = int(
        df[ID_COLUMN].duplicated().sum()
    )

    if duplicate_customer_ids > 0:
        fail(
            "Duplicate customer IDs detected: "
            f"{duplicate_customer_ids}"
        )

    missing_customer_ids = int(
        df[ID_COLUMN].isna().sum()
    )

    if missing_customer_ids > 0:
        fail(
            "Missing customer IDs detected: "
            f"{missing_customer_ids}"
        )

    # ------------------------------------------------------------------------
    # Target
    # ------------------------------------------------------------------------

    target_missing = int(
        df[TARGET_COLUMN].isna().sum()
    )

    if target_missing > 0:
        fail(
            "Missing Churn target values detected: "
            f"{target_missing}"
        )

    observed_target_values = set(
        df[TARGET_COLUMN].unique()
    )

    unexpected_target_values = sorted(
        observed_target_values
        - EXPECTED_TARGET_VALUES
    )

    if unexpected_target_values:
        fail(
            "Unexpected Churn target values detected: "
            f"{unexpected_target_values}"
        )

    print(
        f"Duplicate customer IDs: {duplicate_customer_ids}"
    )

    print(
        f"Missing customer IDs: {missing_customer_ids}"
    )

    print(
        f"Missing target values: {target_missing}"
    )

    print(
        f"Target values: {sorted(observed_target_values)}"
    )

    # ========================================================================
    # 6. Convert TotalCharges
    # ========================================================================

    print("\n[6/9] Validating TotalCharges...")

    if "TotalCharges" not in df.columns:
        fail(
            "Expected column 'TotalCharges' was not found."
        )

    # The original Telco dataset stores TotalCharges as text.
    #
    # Some legitimate rows contain blank TotalCharges values. These occur
    # for customers with no accumulated tenure/charges.
    #
    # We convert them to NaN here but DO NOT impute them here.
    #
    # Imputation must happen inside the modeling Pipeline after the
    # train/holdout split so that holdout information cannot influence
    # preprocessing statistics.

    df["TotalCharges"] = pd.to_numeric(
        df["TotalCharges"],
        errors="coerce",
    )

    total_charges_missing = int(
        df["TotalCharges"].isna().sum()
    )

    print(
        "TotalCharges missing after numeric conversion: "
        f"{total_charges_missing}"
    )

    if total_charges_missing > 0:
        print(
            "These missing values will be handled by the modeling "
            "preprocessing pipeline using training data only."
        )
    else:
        print(
            "No TotalCharges missing values detected."
        )

    # ========================================================================
    # 7. Define leakage-safe model features
    # ========================================================================

    print("\n[7/9] Defining leakage-safe model features...")

    feature_columns = [
        column
        for column in df.columns
        if column not in {
            ID_COLUMN,
            TARGET_COLUMN,
        }
    ]

    # ------------------------------------------------------------------------
    # Defensive checks
    # ------------------------------------------------------------------------

    if ID_COLUMN in feature_columns:
        fail(
            f"Identifier column '{ID_COLUMN}' was incorrectly included "
            "in model features."
        )

    if TARGET_COLUMN in feature_columns:
        fail(
            f"Target column '{TARGET_COLUMN}' was incorrectly included "
            "in model features."
        )

    leakage_in_features = sorted(
        FORBIDDEN_LEAKAGE_COLUMNS.intersection(
            feature_columns
        )
    )

    if leakage_in_features:
        fail(
            "Leakage-sensitive columns found in model features: "
            f"{leakage_in_features}"
        )

    print(
        f"Model feature count: {len(feature_columns)}"
    )

    print(
        "customerID excluded from model features: YES"
    )

    print(
        "Churn excluded from model features: YES"
    )

    print("\nModel features:")

    for number, column in enumerate(
        feature_columns,
        start=1,
    ):
        print(
            f"  {number:02d}. {column}"
        )

    # ========================================================================
    # 8. Create stratified train/holdout split
    # ========================================================================

    print(
        "\n[8/9] Creating stratified train/holdout split..."
    )

    # X contains ONLY model features.
    X = df[feature_columns].copy()

    # y contains ONLY the target.
    y = df[TARGET_COLUMN].copy()

    X_train, X_holdout, y_train, y_holdout = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    train_rows = len(X_train)
    holdout_rows = len(X_holdout)

    overall_churn_rate = float(
        (y == "Yes").mean()
    )

    train_churn_rate = float(
        (y_train == "Yes").mean()
    )

    holdout_churn_rate = float(
        (y_holdout == "Yes").mean()
    )

    print(
        f"Training rows: {train_rows:,}"
    )

    print(
        f"Untouched holdout rows: {holdout_rows:,}"
    )

    print(
        f"Overall churn rate: {overall_churn_rate:.4%}"
    )

    print(
        f"Training churn rate: {train_churn_rate:.4%}"
    )

    print(
        f"Holdout churn rate: {holdout_churn_rate:.4%}"
    )

    # ========================================================================
    # 9. Majority-class baseline
    # ========================================================================

    print(
        "\n[9/9] Calculating majority-class baseline..."
    )

    # Determine the majority class ONLY from training data.
    majority_class = y_train.mode().iloc[0]

    # Predict that class for every untouched holdout observation.
    baseline_predictions = pd.Series(
        majority_class,
        index=y_holdout.index,
    )

    baseline_accuracy = float(
        (baseline_predictions == y_holdout).mean()
    )

    actual_churn_count = int(
        (y_holdout == "Yes").sum()
    )

    predicted_churn_count = int(
        (baseline_predictions == "Yes").sum()
    )

    true_positive_count = int(
        (
            (baseline_predictions == "Yes")
            & (y_holdout == "Yes")
        ).sum()
    )

    if actual_churn_count > 0:
        baseline_churn_recall = (
            true_positive_count
            / actual_churn_count
        )
    else:
        baseline_churn_recall = 0.0

    print(
        f"Majority class: {majority_class}"
    )

    print(
        f"Baseline holdout accuracy: "
        f"{baseline_accuracy:.4%}"
    )

    print(
        f"Baseline churn recall: "
        f"{baseline_churn_recall:.4%}"
    )

    # ========================================================================
    # Create report
    # ========================================================================

    REPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    report = {
        "project": "ChurnGuard",
        "stage": "data_preparation",
        "status": "validated",

        "dataset": {
            "path": str(DATA_PATH),
            "rows": int(len(df)),
            "columns": int(len(df.columns)),
            "column_names": list(df.columns),
        },

        "target": {
            "column": TARGET_COLUMN,
            "allowed_values": sorted(
                EXPECTED_TARGET_VALUES
            ),
            "observed_values": sorted(
                observed_target_values
            ),
            "class_counts": {
                str(key): int(value)
                for key, value in (
                    y.value_counts()
                    .sort_index()
                    .to_dict()
                    .items()
                )
            },
            "overall_churn_rate": overall_churn_rate,
        },

        "identifier": {
            "column": ID_COLUMN,
            "duplicate_count": duplicate_customer_ids,
            "missing_count": missing_customer_ids,
            "excluded_from_model_features": True,
        },

        "leakage_checks": {
            "forbidden_columns": sorted(
                FORBIDDEN_LEAKAGE_COLUMNS
            ),
            "forbidden_columns_present": (
                leakage_columns_present
            ),
            "passed": (
                len(leakage_columns_present) == 0
            ),
        },

        "data_quality": {
            "total_charges_missing_after_numeric_conversion": (
                total_charges_missing
            ),
            "total_charges_imputation_stage": (
                "modeling_pipeline_after_split"
            ),
            "target_missing": target_missing,
            "customer_id_missing": missing_customer_ids,
        },

        "features": {
            "count": len(feature_columns),
            "columns": feature_columns,
            "customer_id_excluded": True,
            "target_excluded": True,
        },

        "split": {
            "method": "train_test_split",
            "test_size": TEST_SIZE,
            "random_state": RANDOM_STATE,
            "stratified": True,
            "train_rows": train_rows,
            "holdout_rows": holdout_rows,
            "train_churn_rate": train_churn_rate,
            "holdout_churn_rate": holdout_churn_rate,
        },

        "baseline": {
            "type": "majority_class",
            "majority_class": majority_class,
            "holdout_accuracy": baseline_accuracy,
            "holdout_churn_recall": baseline_churn_recall,
            "holdout_actual_churn_count": actual_churn_count,
            "holdout_predicted_churn_count": predicted_churn_count,
        },
    }

    with REPORT_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            report,
            file,
            indent=2,
        )

    # ========================================================================
    # Final acceptance output
    # ========================================================================

    print("\n" + "=" * 72)
    print("DATA PREPARATION PASSED")
    print("=" * 72)

    print(
        f"Dataset rows:             {len(df):,}"
    )

    print(
        f"Model features:           {len(feature_columns)}"
    )

    print(
        f"Training rows:            {train_rows:,}"
    )

    print(
        f"Untouched holdout rows:   {holdout_rows:,}"
    )

    print(
        f"Overall churn rate:       {overall_churn_rate:.4%}"
    )

    print(
        f"Training churn rate:      {train_churn_rate:.4%}"
    )

    print(
        f"Holdout churn rate:       {holdout_churn_rate:.4%}"
    )

    print(
        f"Majority class:           {majority_class}"
    )

    print(
        f"Baseline accuracy:        {baseline_accuracy:.4%}"
    )

    print(
        f"Baseline churn recall:    {baseline_churn_recall:.4%}"
    )

    print(
        f"TotalCharges missing:     {total_charges_missing}"
    )

    print(
        "\nReport written to:"
        f"\n  {REPORT_PATH}"
    )

    print(
        "\nData-preparation gate: PASS"
    )


if __name__ == "__main__":
    main()