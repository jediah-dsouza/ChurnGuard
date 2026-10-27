# Customer Detail acceptance evidence

## Scope

Vertical Slice 4 implements the Streamlit-compatible Customer Detail route:

```text
/app/customer-detail?fixture={customerId}
```

The current Streamlit 1.50 router does not support nested dynamic `/app/customers/[id]` paths. The query-parameter route was explicitly approved for this frontend implementation. No proxy, URL rewriting, alternate framework, backend, or architectural replacement was added.

Feature checkpoint: `93ad934 — feat: prove churnguard customer detail slice`.

Batch, Analytics, Model, Evaluation, Monitoring, Settings, public pages, backend, ML, persistence, authentication, and deployment remain deferred.

## What was built

- A routed Customer Detail operational record integrated with the existing shell.
- Resolution and safe validation of the `fixture` query parameter.
- Valid behavior for all four approved deterministic customer fixtures.
- Missing-fixture, unknown-fixture, malformed-fixture, and recoverable data-error states.
- Customer header with identity, account context, risk, timestamp, and demo status.
- Prominent risk brief with probability, textual risk classification, threshold, meter, and fixture-specific interpretation.
- Three ranked signed fixture drivers with direction, contribution, explanation, and directly supported customer values.
- Customer-specific plain-English explanation, including conflicting-signal wording for the hard case.
- Deterministic retention recommendation clearly separated from the prediction.
- Customer, Account, and Services context grouped in ruled definition lists.
- Prediction ID, timestamp, threshold, model version, fixture source, and demo-service context.
- Navigation back to Customer History, into the selected fixture in Prediction Workspace, and to Command Center.
- Customer History inspection actions now open Customer Detail first.
- Typed `CustomerDetailResult`, `MockCustomerDetailService`, not-found contract, and safe data-error contract.

## Deterministic data integrity

No customer, prediction, driver, explanation, recommendation, timestamp, model metadata, or performance claim was added outside the supplied fixture contract.

- `CUST-LOW-001` — 11%, Low.
- `CUST-HIGH-001` — 87%, High.
- `CUST-BORDERLINE-001` — 52%, Medium / Review.
- `CUST-HARD-001` — 61%, High and review-worthy.

Driver context is shown only when the driver label maps directly to an available fixture value, such as contract, tenure, payment method, monthly charges, or device protection.

## Automated verification

Commands:

```bash
python -m compileall -q frontend tests
python -m pytest -q
```

Result: 56 tests passed.

The suite covers:

- all four deterministic Customer Detail fixtures;
- unchanged risk outputs;
- fixture-backed driver context;
- identity, risk, drivers, explanation, recommendation, account/service context, and metadata rendering;
- missing, unknown, malformed, and recoverable-error states;
- navigation contracts;
- updated Customer History inspection links;
- every previously accepted Command Center, Customer Analysis, Customer History, validation, and service test.

## Runtime and browser QA

Command:

```bash
npm run visual:qa
```

Result: 27 captured states passed.

Verified:

- high-risk Customer Detail at 375, 768, 1024, and 1440px;
- mobile driver hierarchy and desktop customer-context region;
- low-risk, borderline, and hard-case records;
- missing-fixture, unknown-fixture, and recoverable data-error states;
- Customer History → Customer Detail → Prediction Workspace;
- accepted 87% High prediction result after handoff;
- Command Center and Customer History regressions;
- zero application console/page errors;
- zero horizontal-overflow findings;
- zero visible unnamed interactive controls.

Streamlit performs unsuccessful relative `_stcore` bootstrap probes when a routed page is opened directly under the configured base path. The browser audit records those framework probes separately from application console, page, and HTTP errors; they do not affect page rendering or interaction.

## Responsive verification

- **375px:** customer identity and risk lead; explanation and ranked drivers follow; no desktop table or horizontal overflow.
- **768px:** single-column decision flow preserves risk-first hierarchy.
- **1024px:** balanced risk/explanation split with dense driver ledger.
- **1440px:** persistent command rail, compact operational summary, driver ledger, recommendation, grouped context, and prediction metadata.

## Accessibility

- One H1 per rendered state and logical section headings.
- Native, labeled data-state control.
- Named navigation actions with customer-specific Prediction Workspace text.
- Ordered semantic driver list with three records.
- Customer context grouped into three labeled sections and definition lists.
- Risk communicated with percentage, label, symbol, interpretation, and color.
- Keyboard navigation and visible focus verified.
- Primary targets remain at least 44px.
- Reduced-motion behavior verified.
- Missing, unknown, malformed, and error states provide meaningful text and recovery navigation.

## Anti-Slop review

Passed:

- no generic CRM profile or avatar treatment;
- no floating KPI-card grid;
- no decorative chart, gradient, glassmorphism, illustration, activity feed, fake metric, or AI sparkle treatment;
- no excessive pills or ornamental icons;
- the page follows customer → risk → why → action → context → metadata.

## Defects found and fixed

1. The first browser pass captured one transient Streamlit route-fallback warning. A complete repeat run passed with zero application console/page errors.
2. History inspection initially targeted the prior direct Prediction Workspace route. It now opens Customer Detail, which explicitly hands the same fixture into Prediction Workspace.
3. Browser QA was extended to distinguish known Streamlit bootstrap probes from application errors while still failing on genuine page, console, or HTTP failures.

## Known limitations

- Customer Detail is limited to the four approved deterministic fixtures.
- The route uses the current Streamlit frontend’s approved `fixture` query-parameter contract.
- There is one fixed fixture prediction timestamp and no historical time series.
- Recommendations are deterministic decision-support fixtures and are not claims of proven churn reduction.

## Gate

`PASS — Customer Detail vertical slice proven`