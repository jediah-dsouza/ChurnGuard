# Command Center acceptance evidence

Status values: `PASS`, `FAIL`, `BLOCKED`, `NOT APPLICABLE`.

## Scope

Vertical Slice 2 only: `/app` Command Center. The accepted customer-analysis slice at `/app/predict` remains accepted and is regression-tested.

## Functional acceptance

- Command Center header and deterministic snapshot context: `PASS`
- Four derived KPIs: `PASS`
- Priority queue with all required fields and inspect actions: `PASS`
- Low / Medium-Watch / High distribution with supplied 50% threshold: `PASS`
- Recent fixed-fixture activity ledger: `PASS`
- Honest pre-ML model-health state: `PASS`
- Borderline, hard-case, incomplete-input, and service-failure review states: `PASS`
- Empty history and malformed snapshot states: `PASS`
- Inspect action opens the selected fixture in `/app/predict`: `PASS`

## Deterministic calculations

| Metric | Result | Derivation |
|---|---:|---|
| Predictions analyzed | 4 | Four approved fixtures |
| High-risk customers | 2 | `CUST-HIGH-001`, `CUST-HARD-001` |
| Average predicted risk | 52.75% | `(11 + 87 + 52 + 61) / 4` |
| High-risk share | 50% | `2 / 4` |
| Distribution | Low 1 / Watch 1 / High 2 | Fixture labels |
| Priority order | High 87, High 61, Watch 52, Low 11 | Band priority, then descending probability |

All timestamps are the shared fixed fixture timestamp. No production recency or live activity is implied.

## Automated tests

Command: `.venv/bin/python -m pytest -q`

Coverage:

- snapshot history loading
- KPI calculations
- distribution
- priority ordering
- Command Center render
- inspect-link contract
- empty state
- malformed state
- every accepted Slice 1 test

## Runtime and routes

- `/app`: `PASS`
- `/app/predict`: `PASS`
- Streamlit startup: `PASS`
- Runtime and console errors: `PASS` — zero browser console/page errors

## Responsive and visual QA

Target widths: 375, 768, 1024, 1440px.

Browser command: `node scripts/visual_qa.mjs`

Result: `PASS` — 11 screenshots, four target widths, zero horizontal-overflow findings, zero unnamed visible controls, six named customer-inspection links, and one semantic priority-queue table.

Evidence covers Command Center overview, mobile queue, lower analysis, empty state, malformed state, inspect navigation, and prediction regression.

## Accessibility

- Semantic headings: `PASS`
- Named inspect actions: `PASS`
- Queue table role and mobile labels: `PASS`
- Visible focus: `PASS`
- Risk text plus symbol plus color: `PASS`
- Reduced motion: `PASS`
- Contrast tokens: `PASS`
- Horizontal overflow: `PASS`

## Anti-Slop review

- No fabricated customers, activity, model quality, or production status.
- KPI strip is a connected ledger, not generic floating cards.
- Distribution uses direct counts appropriate to four fixtures.
- Model health explicitly states that evaluation is pending.
- Demo/test states are labeled and separated from customer predictions.

## Regression and build

- `.venv/bin/python -m compileall -q frontend tests`: `PASS`
- `.venv/bin/python -m pytest -q`: `PASS` — 24 tests
- All 17 accepted customer-analysis tests remain passing.

## Gate

**PASS — Command Center vertical slice proven.**

The customer-analysis acceptance status remains unchanged. Git checkpoint is recorded in the final handoff.