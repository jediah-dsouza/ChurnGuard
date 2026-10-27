# Model Status acceptance evidence

## Scope and purpose

Vertical Slice 7 implements only:

```text
/app/model
```

The Model Intelligence / Model Status workspace helps a retention operator or technical reviewer determine what model information can be trusted now. Its primary conclusion is explicit: the deterministic fixture contract is available, but no trained or production model is connected.

Model Explanations, Evaluation, Monitoring, Settings, public pages, FastAPI, authentication, real inference, training, tuning, SHAP, MLflow integration, model persistence, and deployment remain deferred.

## Implemented sections

1. Frontend-demo boundary and source context.
2. Current operational status:
   - trained model not connected;
   - deterministic fixture contract available or unavailable;
   - production model not deployed.
3. Model identity:
   - selected model;
   - model family;
   - model version;
   - training date;
   - experiment tag.
4. Threshold and classification context.
5. Configuration and artifact status:
   - feature count;
   - engineered-feature count;
   - minimum engineered features planned;
   - calibration;
   - serialization;
   - planned serialization formats;
   - MLflow reference and status.
6. Planned training-data description.
7. Required candidate comparison:
   - Majority baseline;
   - Logistic Regression;
   - Random Forest;
   - XGBoost;
   - Accuracy, Precision, Recall, F1, ROC-AUC, and PR-AUC columns.
8. Explicit Evidence boundary for Evaluation, Explanations, and Operations.

No performance chart, confusion matrix, calibration plot, SHAP view, feature-importance chart, monitoring value, health percentage, latency, uptime, or production usage metric was added.

## Service architecture

```text
Model UI
  → ModelService
  → MockModelService
  ├── MockPredictionService
  │     → CHURNGUARD_SAMPLE_DATA.json
  └── ChurnGuard_Master_JSON_Prompt.json
        → approved future-pipeline requirements
```

`MockModelService` owns:

- authoritative source loading;
- fixture-contract version and threshold extraction;
- cross-fixture consistency checks;
- current-value versus planned-requirement separation;
- candidate-model construction;
- unavailable-state construction;
- safe malformed-data errors.

The page owns only state selection and presentation. A future backend metadata adapter can implement the same typed boundary.

## Deterministic model metadata

Available now:

| Field | Value | Source |
|---|---|---|
| Workspace state | Frontend-only demo metadata | Current stage |
| Fixture contract | Available | Approved deterministic fixtures |
| Model version | `demo-fixture-v1.0.0` | Existing fixture prediction contract |
| Threshold | 50% demo marker | Existing fixture prediction contract |
| Minimum engineered features planned | 5 | Master specification |
| Planned serialization formats | joblib, skops | Master specification |
| Planned candidates | Majority baseline, Logistic Regression, Random Forest, XGBoost | Master specification |
| Planned training source | Telco Customer Churn or approved equivalent | Master specification |

Intentionally unavailable:

- selected trained model;
- model family;
- training date;
- experiment tag;
- trained feature count;
- engineered-feature count;
- calibration result;
- serialized artifact;
- MLflow experiment reference;
- every candidate performance metric.

The 50% fixture threshold is described as a reference marker only. The page explicitly states that it has not been selected or optimized through Evaluation.

## States and interactions

States proven:

1. Demo model context.
2. Model unavailable.
3. Malformed model metadata / service error.
4. Recovery to the approved demo context.
5. Incomplete artifact metadata within the normal demo state.

The sidebar state selector is development-only and deterministic. No threshold adjustment, retraining, reevaluation, or model-selection control was introduced because the authoritative specification does not require one in this frontend-only slice.

No artificial loading delay was added; local fixture and specification reads complete immediately.

## Automated tests

Commands:

```bash
python -m compileall -q frontend tests
python -m pytest -q
```

Result: **104 tests passed**.

Fourteen Model tests cover:

- fixture-backed version and threshold;
- absent trained-artifact metadata;
- authoritative pipeline requirements;
- candidate inventory;
- unavailable candidate metrics;
- unavailable current-model state;
- malformed-data error contract;
- page loading;
- demo-data boundary;
- identity and configuration rendering;
- threshold wording;
- candidate comparison;
- future-evidence boundary;
- unavailable state;
- error and recovery;
- Model navigation.

All 90 previously accepted tests remained passing, covering Command Center, Customer Analysis, Customer History, Customer Detail, Batch Prediction, Analytics, validation, and deterministic fixture behavior.

## Browser visual QA

Command:

```bash
npm run visual:qa
```

Result: **57 captured states passed**.

Eight Model captures cover:

- populated Model status at 375, 768, 1024, and 1440px;
- lower candidate/evidence content at 375 and 1440px;
- model-unavailable state;
- malformed/error state and successful recovery.

The full audit also re-ran every accepted route and reported:

- 0 application console/page errors;
- 0 horizontal-overflow findings;
- 0 visible unnamed interactive controls;
- 1 logical Model H1;
- 1 semantic current-status section;
- 5 model-identity values;
- 2 labeled configuration sections;
- 1 semantic candidate table;
- 8 candidate-table headers;
- 4 candidate rows;
- 1 evidence-boundary note;
- visible keyboard focus;
- reduced-motion support.

Known Streamlit relative `_stcore` bootstrap probes are recorded separately from application console, page, and HTTP failures.

## Responsive verification

- **375px:** compact identity, status-first reading order, stacked status facts, two-column identity ledger, single-column threshold/configuration, and vertical candidate summaries.
- **768px:** compact navigation with readable operational status and responsive candidate summaries.
- **1024px:** status and threshold preserve analytical hierarchy while candidates remain vertical instead of forcing a dense comparison table.
- **1440px:** persistent command rail, two-region current status, five-field identity ledger, threshold ruler, paired configuration ledgers, and eight-column semantic candidate table.

No target width produced horizontal page overflow.

## Accessibility

- One H1 and logical H2/H3 hierarchy.
- Semantic status, note, definition-list, table, caption, header, and list structures.
- Risk/model state communicated through text and structure, not color alone.
- Native labeled demo-state control.
- Keyboard-operable navigation, state control, and retry.
- Visible focus verified on the persistent Model navigation action.
- Candidate metric dashes have accessible “Not available” labels.
- Error and unavailable states explain what happened, what remains available, and the next action.
- Primary controls retain appropriate touch targets.
- Reduced-motion behavior verified.
- Existing contrast tokens preserved.

## Design review

### Operator decision

The primary operator question is: **Is a real model configured, and what evidence can I trust?**

The page therefore prioritizes:

1. current operational truth;
2. identity and threshold context;
3. artifact/configuration availability;
4. planned candidates without metrics;
5. explicit future-evidence boundaries.

Raw implementation detail, decorative charts, and unsupported controls were removed from scope.

### Anti-Slop

Passed:

- no generic ML dashboard;
- no floating KPI-card grid;
- no fake terminal, neural-network illustration, sparkle, glow, gradient, or AI branding;
- no fabricated metric or production-health value;
- no selected-model claim;
- no fake model score;
- no fake calibration, SHAP, drift, uptime, latency, or usage;
- the candidate table deliberately shows unavailable metrics rather than placeholder numbers.

### Impeccable and Taste review

Passed:

- the most important truth appears first;
- typography and ruled ledgers carry hierarchy;
- analytical density increases progressively;
- mobile changes representation instead of compressing the desktop table;
- unavailable values are consistent and scannable;
- motion remains absent except existing restrained shared behavior;
- the page uses ChurnGuard’s established mineral canvas, navy rail, amber context, borders, spacing, focus, and responsive patterns.

## Defects found and fixed

1. The unavailable-state QA selector matched both explanatory copy and the exact threshold label. The assertion now targets the exact visible label.
2. The initial focus audit targeted the collapsed sidebar state control. It now verifies visible focus on the persistent Model navigation action.

Both fixes were followed by the complete 104-test suite and full 57-state browser audit.

## Regressions

Verified:

- `/app`;
- `/app/predict`;
- `/app/customers`;
- `/app/customer-detail?fixture=CUST-HIGH-001`;
- `/app/batch`;
- `/app/analytics`;
- `/app/model`.

Deterministic outputs remain unchanged:

- `CUST-LOW-001` — 11%, Low;
- `CUST-HIGH-001` — 87%, High;
- `CUST-BORDERLINE-001` — 52%, Medium / Review;
- `CUST-HARD-001` — 61%, High and review-worthy.

## Limitations and future boundaries

- No trained model exists in this frontend stage.
- `demo-fixture-v1.0.0` identifies the deterministic UI contract, not a serialized trained pipeline.
- The 50% threshold is not optimized or validated.
- Planned candidate names and pipeline requirements are not evidence of completed training.
- Candidate metrics remain unavailable until real training and Evaluation.
- Calibration remains unavailable until Evaluation.
- Global/local SHAP and feature importance remain unavailable until Model Explanations.
- Deployment, latency, uptime, usage, and drift remain unavailable until backend and Monitoring stages.
- No future route was linked before it exists.

## Design-system decision

`design-system/DESIGN.md` was not changed. The Model page reuses established status treatments, ruled definition lists, semantic tables, responsive record summaries, focus behavior, spacing, and reduced-motion rules without introducing a genuinely new reusable design-system primitive.

## Gate

`PASS — Model Status vertical slice proven`