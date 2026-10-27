# Batch Prediction acceptance evidence

## Scope

Vertical Slice 5 implements only:

```text
/app/batch
```

Feature checkpoint: `539a098 — feat: prove churnguard batch prediction slice`.

Analytics, Model, Model Explanations, Evaluation, Monitoring, Settings, public pages, backend, real ML inference, SHAP, MLflow, database, authentication, and deployment remain deferred.

## Implementation

- Batch Prediction route integrated with the existing ChurnGuard shell.
- Deterministic approved-batch source generated from all four version-controlled fixtures.
- Native UTF-8 CSV upload and approved input-template download.
- Visible CSV schema requirements and compact four-field preview.
- Validation summary for total, valid, and invalid records.
- Row-level actionable validation report.
- Disabled analysis action for invalid, empty, or malformed datasets.
- Immediate deterministic analysis with an intentional spinner and no artificial delay.
- Recoverable service-error state preserving the validated dataset.
- Connected five-value result ledger:
  - records analyzed;
  - High;
  - Medium / Watch;
  - Low;
  - average predicted risk.
- Direct-count risk distribution using labeled restrained bars.
- Probability-prioritized semantic desktop results table.
- Responsive customer result summaries at 1024px and below.
- Native customer-specific inspection actions into Customer Detail.
- Deterministic results CSV download.

## Architecture

```text
Batch UI
  → BatchService contract
  → MockBatchService
  → MockPredictionService
  → CHURNGUARD_SAMPLE_DATA.json
```

`MockBatchService` owns:

- approved demo CSV generation;
- schema columns;
- UTF-8 and CSV parsing;
- empty/malformed handling;
- typed `CustomerInput` validation;
- canonical approved-fixture matching;
- batch prediction orchestration;
- summary calculations;
- deterministic probability sorting;
- results CSV generation.

The UI does not contain model calculations. Future HTTP batch transport can replace the mock service behind the typed boundary.

Shared absolute `StreamlitPage` objects preserve the existing router and enable native Batch → Customer Detail switching. The selected fixture is transferred through session state and Customer Detail sets the canonical `fixture` query parameter.

## Input and deterministic data behavior

The approved demo batch contains exactly:

- `CUST-LOW-001`;
- `CUST-HIGH-001`;
- `CUST-BORDERLINE-001`;
- `CUST-HARD-001`.

Uploaded data must:

- be UTF-8 CSV;
- contain every existing `CustomerInput` alias column;
- include at least one record;
- satisfy the existing typed customer schema;
- match an approved fixture exactly.

Unknown or edited customer values are invalid and are never scored. The invalid demo state derives from the supplied missing-customer-ID/tenure validation scenario; no customer or prediction was invented.

## States proven

1. Initial / no dataset selected.
2. Approved dataset selected.
3. Fully valid dataset.
4. Invalid row with actionable report.
5. Empty header-only dataset.
6. Malformed non-UTF-8 input.
7. Uploaded approved CSV.
8. Immediate processing spinner.
9. Successful result summary and priority ordering.
10. Recoverable service error.
11. Retry using the preserved validated dataset.
12. Batch result → Customer Detail inspection.

## Deterministic results

- 4 records analyzed.
- 2 High-risk customers.
- 1 Medium / Watch customer.
- 1 Low-risk customer.
- 52.75% average predicted risk.
- Priority order:
  1. `CUST-HIGH-001` — 87%, High.
  2. `CUST-HARD-001` — 61%, High.
  3. `CUST-BORDERLINE-001` — 52%, Medium / Review.
  4. `CUST-LOW-001` — 11%, Low.

No model accuracy, performance, production-volume, SHAP, or live-activity claim is shown.

## Automated verification

Commands:

```bash
python -m compileall -q frontend tests
python -m pytest -q
```

Result: 75 tests passed.

The 19 Batch tests cover:

- idle state;
- valid deterministic validation;
- invalid row reporting;
- empty data;
- malformed data;
- missing schema columns;
- approved upload;
- edited-row rejection;
- summary calculations;
- risk distribution values;
- priority ordering;
- unchanged fixture predictions;
- invalid/empty run prevention;
- service error and recovery;
- deterministic result export;
- successful page workflow;
- page validation states;
- page error/retry;
- selected fixture preservation for customer inspection.

All 56 previously accepted tests remained passing.

## Browser and visual QA

Command:

```bash
npm run visual:qa
```

Result: 40 captured states passed.

Batch verification included:

- successful results at 375, 768, 1024, and 1440px;
- mobile priority summaries and inspection controls;
- initial state;
- valid validation;
- invalid, empty, and malformed datasets;
- approved CSV upload;
- recoverable error and retry;
- native Batch → Customer Detail navigation;
- all previously accepted Customer Detail, Customer History, Customer Analysis, and Command Center checks.

Final audit:

- 0 application console/page errors;
- 0 horizontal-overflow findings;
- 0 visible unnamed interactive controls;
- 1 logical H1;
- 1 semantic results table;
- 6 result column headers;
- 5 result summary values;
- 3 labeled distribution rows;
- 4 named customer inspection actions;
- visible keyboard focus;
- reduced-motion support.

Known Streamlit relative `_stcore` bootstrap probes are recorded separately from application console, page, and HTTP failures.

## Responsive verification

- **375px:** dataset and primary action lead; validation follows; results become vertical customer summaries with full-width inspection actions.
- **768px:** single-column workflow with compact validation and results.
- **1024px:** intentional responsive summaries; no squeezed desktop table.
- **1440px:** persistent command rail, compact validation, semantic results table, distribution, and inspection controls.

## Accessibility

- Visible labels for source selection and CSV upload.
- Native keyboard-operable select, uploader, buttons, expander, and downloads.
- Validation status uses text and counts, not color alone.
- Row errors are grouped under a named validation report.
- Risk uses textual labels, percentages, symbols, and color.
- Semantic preview and results tables.
- Named customer-specific inspection controls.
- Visible focus and 44px primary targets.
- Reduced-motion behavior verified.
- Contrast correction applied to primary-button text.

## Anti-Slop review

Passed:

- no generic upload-dashboard treatment;
- no giant upload illustration;
- no floating KPI-card grid;
- no decorative charts;
- no gradients or glassmorphism;
- no fake statistics, model claims, or production activity;
- no sparkle imagery or ornamental animation;
- table/list remains the primary operational object.

## Defects found and fixed

1. CSV `SeniorCitizen` values arrived as strings and failed the integer literal contract. The batch adapter now normalizes only `"0"` and `"1"` before typed validation.
2. Responsive QA initially targeted hidden desktop/mobile duplicate records. Assertions now scope to the active presentation.
3. Validation-state QA initially assumed every dataset would become valid. The helper now waits for each intended status.
4. The upload audit initially targeted the visible drop zone rather than the underlying file input. It now exercises the real input.
5. Shared browser state collapsed the command rail between viewport checks. QA returned to isolated contexts while monitoring child pages.
6. Primary Streamlit button paragraph text inherited muted body color. The shared design system now enforces white text on primary actions.
7. Raw inspection links could show a first-navigation Streamlit fallback dialog. Batch now uses native page switching through shared route objects and preserves the canonical fixture URL.

## Regressions

Verified:

- `/app`;
- `/app/predict`;
- `/app/customers`;
- `/app/customer-detail?fixture=CUST-HIGH-001`;
- all deterministic fixture outputs.

## Known limitations

- Uploaded rows must exactly match approved fixtures in this frontend-only stage.
- Invalid batches are blocked rather than partially scored.
- Processing is immediate and local; no production-scale progress estimate is implied.
- Results are not persisted after the session.
- All predictions share the fixed fixture timestamp and demo model version.

## Gate

`PASS — Batch Prediction vertical slice proven`