from pathlib import Path

source = Path("ml/evaluate_nested_cv_rigorous.py")
target = Path("ml/evaluate_nested_cv_thresholds.py")

if target.exists():
    raise SystemExit(f"STOP: {target} already exists.")

text = source.read_text(encoding="utf-8-sig")

replacements = [
    (
        '    metrics_path = REPORT_DIR / "nested_cv_rigorous_fold_metrics_v2.csv"\n'
        '    summary_path = REPORT_DIR / "nested_cv_rigorous_evaluation_v2.json"\n\n'
        '    if metrics_path.exists() or summary_path.exists():\n'
        '        raise FileExistsError(\n'
        '            "Rigorous evaluation output already exists. Preserve it and choose "\n'
        '            "new filenames before running again. No reports were overwritten."\n'
        '        )',
        '    metrics_path = REPORT_DIR / "nested_cv_threshold_fold_metrics_v1.csv"\n'
        '    oof_path = REPORT_DIR / "nested_cv_oof_predictions_v1.csv"\n'
        '    sensitivity_path = REPORT_DIR / "nested_cv_threshold_sensitivity_v1.csv"\n'
        '    summary_path = REPORT_DIR / "nested_cv_threshold_analysis_v1.json"\n\n'
        '    output_paths = [metrics_path, oof_path, sensitivity_path, summary_path]\n'
        '    if any(path.exists() for path in output_paths):\n'
        '        raise FileExistsError("A threshold-analysis output exists; nothing overwritten.")'
    ),
    (
        '    results = []\n    selected_models = []',
        '    results = []\n    selected_models = []\n    oof_predictions = []'
    ),
    (
        '        test_predictions = (test_probabilities >= threshold).astype(int)',
        '        test_predictions = (test_probabilities >= threshold).astype(int)\n'
        '        for row_idx, actual, probability in zip(test_idx, y_test.to_numpy(), test_probabilities):\n'
        '            oof_predictions.append({\n'
        '                "row_index": int(row_idx),\n'
        '                "customerID": str(df.iloc[row_idx][ID]),\n'
        '                "actual_churn": int(actual),\n'
        '                "probability": float(probability),\n'
        '                "outer_fold": int(fold),\n'
        '                "selected_model": selected_name,\n'
        '            })'
    ),
    (
        '    results_df.to_csv(metrics_path, index=False)',
        '    results_df.to_csv(metrics_path, index=False)\n\n'
        '    oof_df = pd.DataFrame(oof_predictions)\n'
        '    if len(oof_df) != len(df) or oof_df["row_index"].duplicated().any():\n'
        '        raise ValueError("Expected exactly one out-of-fold prediction per dataset row.")\n'
        '    oof_df.to_csv(oof_path, index=False)\n\n'
        '    actual = oof_df["actual_churn"].to_numpy(dtype=int)\n'
        '    probabilities = oof_df["probability"].to_numpy(dtype=float)\n'
        '    threshold_rows = []\n'
        '    candidates = np.unique(np.concatenate([np.linspace(0.05, 0.95, 181), [0.5]]))\n'
        '    for candidate in candidates:\n'
        '        predicted = (probabilities >= candidate).astype(int)\n'
        '        tn = int(((actual == 0) & (predicted == 0)).sum())\n'
        '        fp = int(((actual == 0) & (predicted == 1)).sum())\n'
        '        fn = int(((actual == 1) & (predicted == 0)).sum())\n'
        '        tp = int(((actual == 1) & (predicted == 1)).sum())\n'
        '        rec = recall_score(actual, predicted, zero_division=0)\n'
        '        threshold_rows.append({\n'
        '            "threshold": float(candidate),\n'
        '            "accuracy": float(accuracy_score(actual, predicted)),\n'
        '            "precision": float(precision_score(actual, predicted, zero_division=0)),\n'
        '            "recall": float(rec),\n'
        '            "f1": float(f1_score(actual, predicted, zero_division=0)),\n'
        '            "predicted_positive_rate": float(predicted.mean()),\n'
        '            "true_positive": tp, "true_negative": tn,\n'
        '            "false_positive": fp, "false_negative": fn,\n'
        '            "meets_recall_floor": bool(rec >= RECALL_FLOOR),\n'
        '        })\n'
        '    pd.DataFrame(threshold_rows).to_csv(sensitivity_path, index=False)'
    ),
    (
        '    print(f"Fold metrics: {metrics_path}")\n'
        '    print(f"Summary: {summary_path}")',
        '    print(f"Fold metrics: {metrics_path}")\n'
        '    print(f"OOF predictions: {oof_path}")\n'
        '    print(f"Threshold sensitivity: {sensitivity_path}")\n'
        '    print(f"Summary: {summary_path}")'
    ),
]

for old, new in replacements:
    count = text.count(old)
    if count != 1:
        raise SystemExit(
            f"STOP: expected one matching source block, found {count}. "
            "No target script was written."
        )
    text = text.replace(old, new, 1)

# Update the description to accurately describe this additional analysis.
text = text.replace(
    'Rigorous nested CV completed.',
    'Threshold sensitivity analysis completed.',
    1,
)

# Compile in memory before writing anything.
compile(text, str(target), "exec")

target.write_text(text, encoding="utf-8")
print(f"Created and syntax-checked: {target}")
print("Original script and existing reports were not modified.")
