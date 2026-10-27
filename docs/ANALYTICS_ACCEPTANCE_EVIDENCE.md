# Analytics acceptance evidence

## Scope and purpose

Vertical Slice 6 implements only:

```text
/app/analytics
```

Analytics helps a retention operator compare risk concentration in the currently available deterministic customer-risk data. Model, Model Explanations, Evaluation, Monitoring, Settings, public pages, backend, authentication, real ML inference, SHAP, MLflow, database, persistence, and deployment remain deferred.

## Implemented views

- Connected snapshot ledger:
  - 4 approved prediction results;
  - 52.75% average predicted risk;
  - 50% High-risk rate.
- Direct-count risk-band distribution:
  - High: 2;
  - Medium / Watch: 1;
  - Low: 1.
- Prediction volume over the only supplied fixture date:
  - 04 Oct 2026: 4.
- Explicit prediction success/failure availability state.
- Selectable segment ledger for every authoritative, fixture-supported dimension:
  - contract;
  - tenure bucket;
  - internet service;
  - payment method.
- Desktop semantic table and deliberate mobile/tablet record summaries.

No customer drill-down was added because the authoritative Analytics page definition does not require it. Existing Customer Detail behavior remains available through Customer History and Batch Prediction.

## Data sources and deterministic calculations

```text
Analytics UI
  → AnalyticsService
  → MockAnalyticsService
  → MockPredictionService
  → CHURNGUARD_SAMPLE_DATA.json
```

`MockAnalyticsService` derives every result from the four approved fixtures. It owns:

- prediction-row construction;
- date aggregation;
- risk-band counts;
- arithmetic mean risk;
- High-label share;
- segment grouping;
- segment customer counts;
- segment mean risk;
- segment High count and share;
- descending mean-risk ordering with deterministic tie-breaks;
- highest-average segment interpretation.

Confirmed values:

| Measure | Result | Derivation |
|---|---:|---|
| Prediction volume | 4 | Four approved fixture predictions |
| Average predicted risk | 52.75% | `(11 + 87 + 52 + 61) / 4` |
| High-risk rate | 50% | Two High labels / four results |
| Risk distribution | 2 High, 1 Medium, 1 Low | Fixture labels |
| Fixture date volume | 4 on 04 Oct 2026 | Fixed supplied timestamp |

Example segment results:

- Month-to-month: 2 customers, 69.5% average risk, 1 High, 50% High share.
- Electronic check: 2 customers, 74% average risk, 2 High, 100% High share.
- Fiber optic: 3 customers, 66.7% average risk, 2 High, 66.7% High share.
- 13–36 months: 2 customers, 56.5% average risk, 1 High, 50% High share.

The fixture source stores prediction results but no prediction-attempt outcome log. Success/failure rate is therefore displayed as **not available**, not as an inferred 100%.

## Interactions and states

The only Analytics control is the authoritative segment selector. It switches among contract, tenure bucket, internet service, and payment method without changing source records.

States proven:

1. Populated initial Analytics state.
2. Contract segment.
3. Tenure-bucket segment.
4. Internet-service segment.
5. Payment-method segment.
6. Empty Analytics state with a route to Customer Analysis.
7. Malformed-data/service-error state.
8. Recovery to the approved sample snapshot.

No artificial loading delay was added; fixture aggregation is immediate and local.

## Automated tests

Commands:

```bash
python -m compileall -q frontend tests
python -m pytest -q
```

Result: **90 tests passed**.

Fifteen tests were added: fourteen Analytics tests and one router regression test. Analytics coverage includes:

- populated initial state;
- exact summary calculations;
- unchanged fixture outputs;
- one-date volume;
- risk distribution;
- every supported segment;
- deterministic sorting;
- honest outcome unavailability;
- empty contract;
- malformed/error contract;
- unsupported segment rejection;
- page rendering;
- segment interactions;
- empty page state;
- service error and recovery.

All 75 previously accepted tests remained passing, including Command Center, Customer Analysis, Customer History, Customer Detail, and Batch Prediction.

## Browser visual QA

Command:

```bash
npm run visual:qa
```

Result: **49 captured states passed**.

Nine Analytics captures cover:

- populated Analytics at 375, 768, 1024, and 1440px;
- lower segment content at 375 and 1440px;
- payment-method segment state;
- empty state;
- error state and successful recovery.

The full audit also re-ran all prior route checks and reported:

- 0 application console/page errors;
- 0 horizontal-overflow findings;
- 0 visible unnamed interactive controls;
- 1 logical Analytics H1;
- 3 connected summary values;
- 3 labeled risk-distribution rows;
- 1 date-volume row;
- 1 semantic segment table with 5 column headers;
- visible keyboard focus;
- reduced-motion support.

Known Streamlit relative `_stcore` bootstrap probes are recorded separately from application console, page, and HTTP failures.

## Responsive verification

- **375px:** compact identity, one-column analytical reading order, stacked summary measures, labeled bars, explicit unavailable outcome, and vertical segment records.
- **768px:** compact navigation, readable summary ledger, single-column risk distribution, and mobile segment summaries.
- **1024px:** three-value summary remains connected; distribution and volume use a balanced two-column comparison; segment records remain vertical to avoid a squeezed table.
- **1440px:** persistent command rail, bounded analytical width, two-column distribution/volume region, and five-column semantic segment table.

No target width produced horizontal page overflow.

## Accessibility

- One H1 and logical section headings.
- Native labeled segment selector.
- Keyboard-operable selector, sidebar state control, recovery action, and navigation.
- Visible 3px focus treatment.
- Risk communicated by text, counts, percentages, and color.
- Semantic desktop segment table with caption and column headers.
- Mobile segment list preserves segment name, customer count, mean risk, High count, and High share.
- Bars have accessible labels and adjacent text values.
- Empty and error states explain what happened and the next action.
- Reduced-motion behavior verified.
- Existing contrast tokens preserved.

## Anti-Slop review

Passed:

- no generic BI dashboard;
- no floating KPI cards;
- no pie, donut, 3D, decorative, or animated charts;
- no gradients, glassmorphism, sparkle imagery, or ornamental icons;
- no fabricated volume, production rate, revenue, performance, SHAP, or MLflow claims;
- direct counts and ruled ledgers remain primary;
- unavailable outcome data is stated instead of invented;
- copy is specific to the four-customer deterministic fixture set.

## Defects found and fixed

1. The first accessibility audit moved focus away from the segment selector before reading the focus outline. The audit now verifies the focused control directly.
2. Initial viewport captures did not expose the lower outcome and segment regions. Dedicated 375px and 1440px lower-page captures were added and inspected.

Both fixes were followed by the full automated suite and complete browser QA.

## Regressions

Verified:

- `/app`;
- `/app/predict`;
- `/app/customers`;
- `/app/customer-detail?fixture=CUST-HIGH-001`;
- `/app/batch`;
- `/app/analytics`.

Deterministic outputs remain:

- `CUST-LOW-001` — 11%, Low;
- `CUST-HIGH-001` — 87%, High;
- `CUST-BORDERLINE-001` — 52%, Medium / Review;
- `CUST-HARD-001` — 61%, High and review-worthy.

## Limitations

- Four approved customers are not representative of production behavior.
- All results share one fixed fixture timestamp, so volume over time contains one date and is not a trend.
- Prediction-attempt success/failure is unavailable until an outcome log exists.
- Segment results are descriptive fixture summaries, not statistical findings.
- No persistence, backend, real model, evaluation metric, or customer drill-down specific to Analytics was added.

## Architecture and design decisions

- Analytics uses a typed, replaceable `AnalyticsService` boundary.
- All calculations live in `MockAnalyticsService`, not Streamlit components.
- The service composes `MockPredictionService`; no second prediction source exists.
- A selector and ruled ledger communicate four small segment dimensions more accurately than multiple decorative charts.
- `design-system/DESIGN.md` was not changed because Analytics reuses established connected ledgers, labeled bars, responsive record summaries, semantic tables, focus, and reduced-motion patterns without introducing a genuinely new reusable primitive.

## Gate

`PASS — Analytics vertical slice proven`