# Model Explanations acceptance evidence

## Scope and purpose

Vertical Slice 8 implements:

```text
/app/model-explanations?fixture={customerId}
```

The workspace helps a retention operator understand which supplied demo signals raise, lower, or complicate a fixture's churn concern before choosing a response. It contains a global preview across the four approved examples and a local explanation for every approved customer.

The master specification names `/app/model/explanations`. Streamlit 1.50 rejects nested page URL paths, so the current frontend uses the smallest coherent flat adaptation: `/app/model-explanations`. This is a framework routing constraint, not a product-domain decision.

Real SHAP, a trained model, statistically validated global importance, causal claims, Evaluation, Monitoring, FastAPI, authentication, persistence, MLflow, and deployment remain deferred.

## Implemented experience

### Global explanation preview

- Explicit demo-data and non-SHAP disclosure.
- Product question: “What signals are most influential across the current four demo examples?”
- Five ranked driver families:
  1. Contract;
  2. Tenure;
  3. Monthly charges;
  4. Payment method;
  5. Device protection.
- Direction stated in text as higher-risk, lower-risk, or mixed.
- Ordinal relative-influence labels rather than fabricated statistical precision.
- Accessible ranked list plus semantic six-column data table.
- Expandable methodology and limitations.

The ranking sums the absolute contribution magnitudes already supplied in the approved UI fixtures, grouped into the five driver families. Direction becomes mixed when approved fixture examples disagree. Bars are normalized against the highest demo total only for comparison. They are not SHAP values, probabilities, causal effects, or a population estimate.

### Local customer explanation

For all four approved customers:

- customer identifier;
- current deterministic risk and risk level;
- explanation status and fixture version;
- three ranked supplied drivers;
- explicit higher- or lower-risk direction;
- plain-English explanation;
- expandable technical fixture context;
- balancing evidence where present;
- mixed-signal notice where present;
- approved retention recommendation and operator actions;
- links back to Customer Detail and Customer Analysis.

`CUST-HARD-001` explicitly demonstrates competing higher- and lower-risk evidence and instructs the operator to use human review rather than treating the result as one-directional.

## Architecture

```text
Model Explanations UI
  → typed ExplanationService
  → deterministic MockExplanationService
  ├── MockPredictionService
  └── MockCustomerDetailService
        → CHURNGUARD_SAMPLE_DATA.json
```

The page owns selection, query-parameter state, loading feedback, retry actions, and presentation. `MockExplanationService` owns:

- fixture lookup;
- prediction and detail composition;
- local explanation normalization;
- global driver grouping and ordering;
- balancing-factor and mixed-signal detection;
- fixture provenance;
- empty, unavailable, malformed, unknown-customer, and safe service-error behavior.

Typed models include `ExplanationDriverItem`, `GlobalExplanationDriver`, `GlobalExplanationResult`, and `LocalExplanationResult`. The service contract exposes global and local retrieval without coupling the page to the mock implementation.

A future HTTP/backend implementation can replace `MockExplanationService` while preserving the UI contract.

## Deterministic data

Source: `CHURNGUARD_SAMPLE_DATA.json`.

| Customer | Risk | Label | Explanation behavior |
|---|---:|---|---|
| `CUST-LOW-001` | 11% | Low | Lower-risk fixture evidence |
| `CUST-HIGH-001` | 87% | High | Month-to-month, short-tenure, and charge concern |
| `CUST-BORDERLINE-001` | 52% | Medium / Review | Borderline higher- and lower-risk evidence |
| `CUST-HARD-001` | 61% | High | Explicit conflicting-signal review case |

The displayed contribution values and explanations are approved deterministic UI fixtures. They are not computed SHAP output, trained-model evidence, statistical validation, or production explanations.

## States and interactions

Global states:

1. Populated demo preview.
2. Empty dataset.
3. Explanation unavailable.
4. Malformed explanation data.
5. Recoverable service error.
6. Successful retry to populated state.

Local states:

1. Idle / no selected customer.
2. Native loading feedback with no artificial delay.
3. Populated result for every approved customer.
4. No explanation available.
5. Unknown customer query parameter.
6. Malformed explanation data.
7. Recoverable service error.
8. Successful retry preserving the selected customer.

Interactions:

- select an approved customer;
- load its demo explanation;
- expand methodology;
- expand each driver's technical fixture context;
- retry global or local loading;
- navigate from Customer Detail to “Why this prediction?”;
- return to Customer Detail or Customer Analysis.

## Automated tests

Commands:

```bash
python -m compileall -q frontend tests
python -m pytest -q
node --check scripts/visual_qa.mjs
```

Result: **130 tests passed**.

Twenty-six added tests cover:

- typed explanation service behavior;
- successful global ranking;
- global empty, unavailable, malformed, error, and recovery states;
- successful local explanation for all four fixtures;
- unknown customer;
- local unavailable, malformed, error, and recovery states;
- `CUST-HARD-001` conflicting signals;
- route registration and query-parameter loading;
- Customer Detail and Model navigation;
- loading feedback and honesty copy;
- unchanged deterministic prediction outputs.

All 104 previously accepted tests remained passing.

## Browser visual QA

Command:

```bash
npm run visual:qa
```

Result: **77 captured states passed**, including **20 Model Explanations captures**.

Explanation coverage:

1. Populated global/local page at 375, 768, 1024, and 1440px.
2. Lower-page local content at 375 and 1440px.
3. Idle local state.
4. Global empty state.
5. Global unavailable state.
6. Global malformed state.
7. Global service error and recovery.
8. Local `CUST-LOW-001`.
9. Local `CUST-HIGH-001`.
10. Local `CUST-BORDERLINE-001`.
11. Local `CUST-HARD-001`.
12. Unknown customer.
13. Local unavailable state.
14. Local malformed state.
15. Local service error and recovery.
16. Customer Detail → Model Explanations navigation.

The complete audit reported:

- 0 application console/page errors;
- 0 horizontal-overflow findings;
- 0 visible unnamed interactive controls;
- 1 logical H1;
- 1 global ranked list with 5 drivers;
- 1 semantic global table with 6 headers;
- 1 local explanation head with 3 ranked drivers;
- 3 labeled technical disclosures;
- 1 methodology disclosure;
- 1 operator readout;
- textual direction semantics;
- visible keyboard focus;
- reduced-motion support.

Known Streamlit relative `_stcore` bootstrap probes are recorded separately from application failures.

## Responsive verification

- **375px:** compact page header, global ranking retained before the table alternative, deliberate two-column local identity ledger, prominent risk, readable mixed-signal notice, and single-column driver/action flow.
- **768px:** compact navigation and stacked operational content preserve global-to-local order without compressing the semantic table.
- **1024px:** analytical hierarchy remains intact and dense content uses responsive summaries rather than horizontal overflow.
- **1440px:** persistent command rail, full ranked global preview and table, wide local identity/risk treatment, and scan-friendly driver ledger.

No target width produced horizontal page overflow. Long explanation text, driver labels, and operational copy wrapped without clipping.

## Accessibility

- One H1 and logical section hierarchy.
- Native labeled customer selector and buttons.
- Semantic list and table alternatives for global data.
- Higher-risk, lower-risk, and mixed direction always stated in text, not color alone.
- Risk labels combine text, number, and structure.
- Keyboard-operable navigation, selector, buttons, retry actions, and native disclosures.
- Visible focus verified.
- Product-specific idle, unavailable, malformed, unknown, and error messages state what happened and the next action.
- Primary controls retain appropriate touch targets.
- Reduced-motion behavior verified.
- Existing contrast tokens preserved.

## Design review

### Operator decision

The primary question is: **Why is this fixture risky, which evidence complicates that result, and what should the retention operator consider next?**

The page prioritizes:

1. honest demo provenance;
2. global pattern orientation;
3. current customer and risk;
4. ranked drivers and balancing evidence;
5. mixed-signal interpretation;
6. operational readout and next actions.

Academic ML detail, decorative charts, and unsupported confidence or performance metrics were excluded.

### Anti-Slop

Passed:

- no AI branding, brain illustration, sparkle, glow, gradient, fake terminal, or decorative ML chart;
- no fabricated SHAP, population, causal, confidence, or production claim;
- no generic KPI-card grid;
- no misleading numeric precision in the global view;
- every major component answers a retention-operator question;
- ChurnGuard fixture provenance and risk semantics remain explicit.

### Impeccable and Taste

Passed:

- operational truth and the selected customer's risk are visually dominant;
- typography, ruled ledgers, restraint, and progressive density preserve the established ChurnGuard language;
- global and local content have distinct jobs instead of repeated cards;
- mobile changes representation and reading order rather than shrinking desktop;
- error and unavailable states retain context and recovery;
- interactions are native and purposeful;
- no motion was added beyond existing restrained shared behavior.

## Defects found and fixed

1. Streamlit 1.50 rejected the authoritative nested page path. The route was adapted to `/app/model-explanations` and the constraint documented.
2. The first retry implementation attempted to mutate a state key after its widget had been instantiated. Recovery now loads the approved sample directly without unsafe widget mutation.
3. Browser helpers initially assumed only successful local content. They now recognize unavailable and error states before interacting.
4. A cold first navigation to the new page could emit Streamlit's transient route fallback message. The QA runner now warms the registered router before direct route checks; the complete run reports zero application errors.

Every fix was followed by the full 130-test suite and 77-state browser audit.

## Regressions

Verified:

- `/app`;
- `/app/predict`;
- `/app/customers`;
- `/app/customer-detail?fixture=CUST-LOW-001`;
- `/app/customer-detail?fixture=CUST-HIGH-001`;
- `/app/customer-detail?fixture=CUST-BORDERLINE-001`;
- `/app/customer-detail?fixture=CUST-HARD-001`;
- `/app/batch`;
- `/app/analytics`;
- `/app/model`;
- `/app/model-explanations`.

Deterministic outputs remain unchanged:

- `CUST-LOW-001` — 11%, Low;
- `CUST-HIGH-001` — 87%, High;
- `CUST-BORDERLINE-001` — 52%, Medium / Review;
- `CUST-HARD-001` — 61%, High with conflicting-signal review wording.

## Limitations and future boundary

- No trained model or real explanation engine exists.
- Global ranking covers four supplied fixtures and is not statistically representative.
- Contribution magnitudes are illustrative UI fixtures, not SHAP values.
- Explanations describe supplied associations, not causality.
- Real global/local SHAP computation, validation, backend transport, persistence, authentication, MLflow, Evaluation, Monitoring, and deployment remain deferred.
- `/app/model-explanations` is a Streamlit route adaptation of the authoritative `/app/model/explanations` path.

## Design-system decision

`design-system/DESIGN.md` was not changed. The slice reuses established ChurnGuard callouts, ruled ledgers, semantic tables, responsive summaries, risk treatments, disclosures, focus behavior, spacing, and reduced-motion rules without introducing a genuinely new shared primitive.

## Gate

`PASS — Model Explanations vertical slice proven`