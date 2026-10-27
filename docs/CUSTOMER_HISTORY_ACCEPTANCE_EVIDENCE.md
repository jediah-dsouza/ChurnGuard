# Customer History acceptance evidence

## Scope

Vertical Slice 3 implements only `/app/customers`. Customer detail, Batch, Analytics, Model, Evaluation, Monitoring, Settings, public pages, backend, ML, persistence, authentication, and deployment remain deferred.

Source checkpoint declared with the supplied archive: `94bfc4 — docs: add complete project changelog`. The archive did not include `.git` metadata, so its baseline history was reconstructed locally before creating the dedicated feature checkpoint.

Feature checkpoint: `6d941e8 — feat: prove churnguard customer history slice`.

## What was built

- Customer History header with explicit deterministic-demo, service, model-version, and fixed fixture-snapshot context.
- Accessible customer search across fixture-backed customer ID, top driver, contract, and scenario fields, with a clear action.
- Risk filtering for All, Low, Watch / Medium, and High.
- Contract options derived only from fixture values.
- Deterministic tenure buckets: 0–12, 13–36, and 37+ months.
- Prediction-date filtering based only on the fixed fixture timestamp.
- Highest-risk, lowest-risk, newest, and oldest deterministic sorting with customer-ID tie-breaks.
- Combined-filter behavior and separate search-empty and filter-empty recovery states.
- Populated, empty-history, and recoverable malformed-history states.
- A nine-field semantic desktop table and deliberate responsive record summaries.
- Named inspection actions that load the selected fixture in the existing `/app/predict` workflow.
- A typed `CustomerHistoryQuery`, `CustomerHistoryResult`, and `MockCustomerHistoryService` boundary.

Pagination and export were not added: four approved records do not justify either control.

## Authoritative sample data

No customers, probabilities, timestamps, model versions, metrics, or production activity were added. The history uses only:

- `CUST-LOW-001` — 11%, Low, 48 months, Two year.
- `CUST-HIGH-001` — 87%, High, 4 months, Month-to-month.
- `CUST-BORDERLINE-001` — 52%, Medium / Watch, 14 months, Month-to-month.
- `CUST-HARD-001` — 61%, High and review-worthy, 36 months, One year.

All records use the existing fixed `04 Oct 2026 · 18:52 UTC` demo timestamp and `demo-fixture-v1.0.0`.

## Automated verification

Commands:

```bash
python -m compileall -q frontend tests
python -m pytest -q
```

Result: 40 tests passed. The suite covers history loading, all records, search, no search match, risk/contract/tenure/date filters, sorting, combined filters, empty/error contracts, no-results UI, inspection links, selected-fixture handoff, and all 24 previously accepted tests.

## Browser and responsive QA

Command:

```bash
npm run visual:qa
```

Verified:

- populated history at 375, 768, 1024, and 1440px;
- intentional record summaries at 375, 768, and 1024px;
- semantic nine-column history table at 1440px;
- search, clear, individual filters, combined filters, date selection, and sorting;
- search-empty, filter-empty, empty-history, and recoverable-error states;
- Customer History → selected customer → `/app/predict`;
- 87% High result for `CUST-HIGH-001` in the accepted prediction workflow;
- Command Center regression;
- zero application console/page errors;
- zero horizontal-overflow findings;
- zero visible unnamed interactive controls.

Streamlit 1.50 performs two unsuccessful relative `_stcore` bootstrap probes when a nested route is opened directly under a configured base path. The QA audit records these framework probes separately from application console/page errors; they do not affect rendering, routing, or interaction.

## Accessibility

- One logical H1 and semantic section headings.
- Visible search label and native labeled filter controls.
- Semantic desktop table with nine column headers.
- Mobile list structure retaining customer, textual risk, probability, driver, and named action.
- Risk communicated by text and symbol as well as color.
- Keyboard focus and a visible focus outline verified.
- Touch targets remain at least 44px for primary controls.
- Reduced-motion media behavior verified.
- Empty and error messages provide explicit recovery actions.

## Anti-Slop review

Passed. The history ledger is the primary object. No floating KPI-card grid, decorative chart, gradient, glassmorphism, ornamental illustration, fake metric, invented volume, or generic AI-dashboard treatment was added.

## Defects found and fixed

1. The desktop table initially contributed hidden width at mobile breakpoints because routed pages did not reliably receive the shared stylesheet. The application shell now injects the design system on every route; mobile overflow is zero.
2. Streamlit’s generated route navigation appeared above the ChurnGuard command rail. It is now hidden so the established navigation remains the sole shell.
3. Browser-QA selectors initially targeted hidden desktop duplicates on mobile and exact select names that Streamlit expands with current values. The audit now targets the visible responsive record and stable accessible-name suffixes.

## Known limitations

- The fixture set contains four records and one shared authoritative prediction date.
- Newest/oldest sorting is deterministic but ties resolve by customer ID until fixtures provide distinct timestamps.
- This is frontend-only demo history; there is no persistence or production data.

## Gate

`PASS — Customer History vertical slice proven`