# Changelog

All notable changes to the ChurnGuard frontend are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). The project is still in frontend-only development; no entry below represents real model inference, production data, or a deployed backend.

## [Unreleased]

No unreleased product slice is currently in progress.

## [0.8.0] — 2026-10-05

### Vertical Slice 8 — Model Explanations

Feature checkpoint: `16ca21e — feat: prove churnguard model explanations slice`

Acceptance-documentation checkpoint: `e53034b — docs: record churnguard model explanations acceptance`

#### Added

- Added `/app/model-explanations` to the router and established ChurnGuard command rail.
- Added typed `ExplanationService`, safe explanation errors, deterministic `MockExplanationService`, and global/local explanation models.
- Added a fixture-derived global explanation preview with five ranked driver families, explicit direction, ordinal relative influence, readable bars, semantic table, and methodology disclosure.
- Added local explanations for all four approved customers with current risk, three ranked drivers, plain-English meaning, technical fixture context, balancing evidence, mixed-signal handling, and operational recommendations.
- Added explicit demo provenance and non-SHAP, non-causal, non-population wording.
- Added idle/loading, populated, empty, unavailable, unknown-customer, malformed, recoverable-error, and retry/recovery states.
- Added “Why this prediction?” integration from Customer Detail and explanation navigation from Model.
- Added twenty-six tests for the explanation contract, fixtures, states, route, navigation, recovery, and unchanged prediction outputs.
- Expanded browser QA to 77 captured states, including 20 Model Explanations captures.
- Added `docs/MODEL_EXPLANATIONS_ACCEPTANCE_EVIDENCE.md`.

#### Changed

- Updated `README.md` and `docs/ARCHITECTURE.md` for the accepted explanation route and replaceable Explanation service boundary.
- Adapted the master specification's nested `/app/model/explanations` route to `/app/model-explanations` because Streamlit 1.50 rejects nested page paths.
- Expanded browser QA to cover global and local explanation states, all four fixtures, customer-detail integration, recovery, semantic structures, keyboard focus, reduced motion, and 375, 768, 1024, and 1440px viewports.
- Preserved `design-system/DESIGN.md` because the explanation workspace reuses established patterns without adding a genuinely new shared primitive.

#### Fixed

- Reworked retry handling so recovery does not mutate an already-instantiated Streamlit widget state.
- Hardened visual-QA helpers for local unavailable and error states.
- Warmed the registered router before direct route checks to avoid a cold-navigation fallback message.

#### Verified

- Python compilation and visual-QA script syntax passed.
- Full suite passed: 130 tests.
- All 104 previously accepted tests remained passing.
- Browser QA passed: 77 captured states, including 20 explanation captures.
- All four deterministic fixture outputs remained unchanged.
- All eight routes passed with zero application console/page errors, zero horizontal overflow, zero visible unnamed controls, visible keyboard focus, and reduced-motion support.
- No trained SHAP, statistical feature-importance, causal, model-performance, or production explanation claim was introduced.
- Accessibility, Anti-Slop, Impeccable, and Taste reviews passed.

## [0.7.0] — 2026-10-05

### Vertical Slice 7 — Model Intelligence / Model Status

Feature checkpoint: `662fa9c — feat: prove churnguard model slice`

Acceptance-documentation checkpoint: `7cc8558 — docs: record churnguard model acceptance`

#### Added

- Added `/app/model` to the router and established ChurnGuard command rail.
- Added typed `ModelService`, safe `ModelServiceError`, deterministic `MockModelService`, `ModelSnapshot`, and `ModelCandidateRow`.
- Added a status-first Model workspace that distinguishes the available deterministic fixture contract from a trained or production model.
- Added model identity fields for selected model, family, version, training date, and experiment tag.
- Added a 50% fixture-threshold reference with explicit non-optimization wording.
- Added feature-count, engineered-feature, calibration, serialization, MLflow, and training-data status.
- Added the authoritative Majority baseline, Logistic Regression, Random Forest, and XGBoost candidate inventory.
- Added Accuracy, Precision, Recall, F1, ROC-AUC, and PR-AUC comparison fields without fabricated values.
- Added explicit Evaluation, Explanation, and operational evidence boundaries.
- Added demo, unavailable, malformed/error, recovery, and incomplete-metadata states.
- Added semantic desktop candidate table and responsive mobile/tablet candidate summaries.
- Added fourteen Model tests.
- Expanded browser QA to 57 captured states, including eight Model captures.
- Added `docs/MODEL_ACCEPTANCE_EVIDENCE.md`.

#### Changed

- Updated `README.md` and `docs/ARCHITECTURE.md` for the accepted Model route and replaceable Model service boundary.
- Expanded browser QA to cover Model at 375, 768, 1024, and 1440px; unavailable/error/recovery states; semantic structures; keyboard focus; reduced motion; and all accepted regressions.
- Preserved `design-system/DESIGN.md` because the Model page reuses established patterns without adding a genuinely new shared primitive.

#### Fixed

- Corrected unavailable-state browser QA to target the exact threshold-availability label.
- Corrected Model focus QA to inspect the visible persistent navigation action rather than a collapsed sidebar control.

#### Verified

- Python compilation passed.
- Full suite passed: 104 tests.
- All 90 previously accepted tests remained passing.
- Browser QA passed: 57 captured states.
- Model metadata remained deterministic: demo version `demo-fixture-v1.0.0`, 50% reference threshold, four planned candidates, and no trained-artifact metadata.
- All seven routes passed with zero application console/page errors, zero horizontal overflow, zero visible unnamed controls, visible keyboard focus, and reduced-motion support.
- Existing fixture outputs remained unchanged.
- Anti-Slop, Impeccable, and Taste reviews passed.

## [0.6.0] — 2026-10-05

### Vertical Slice 6 — Analytics

Feature checkpoint: `b9e9ac6 — feat: prove churnguard analytics slice`

Acceptance-documentation checkpoint: `5647d02 — docs: record churnguard analytics acceptance`

The supplied archive did not contain `.git` metadata. Its accepted source was recorded locally as baseline `cc20357 — chore: restore supplied proven frontend baseline` before Vertical Slice 6 work began.

#### Added

- Added `/app/analytics` to the router and established ChurnGuard command rail.
- Added typed `AnalyticsService`, safe `AnalyticsServiceError`, deterministic `MockAnalyticsService`, and Analytics snapshot/segment/time-point models.
- Added fixture-derived prediction volume, average predicted risk, High-risk rate, risk-band distribution, and one-date volume view.
- Added authoritative segment breakdowns for contract, tenure bucket, internet service, and payment method.
- Added deterministic segment counts, mean risk, High count/share, ordering, and highest-average interpretation in the service layer.
- Added an explicit unavailable state for prediction success/failure because no outcome log exists.
- Added populated, empty, malformed/service-error, and recovery states.
- Added semantic desktop segment tables and responsive mobile/tablet segment records.
- Added fourteen Analytics tests and one route-regression test.
- Expanded browser QA to 49 captured states, including nine Analytics captures.
- Added `docs/ANALYTICS_ACCEPTANCE_EVIDENCE.md`.

#### Changed

- Updated `README.md` and `docs/ARCHITECTURE.md` for the accepted Analytics route and service boundary.
- Expanded the complete browser audit to cover Analytics at 375, 768, 1024, and 1440px, segment interaction, empty/error/recovery behavior, semantic structure, keyboard focus, reduced motion, and regression routes.
- Preserved `design-system/DESIGN.md`; Analytics reuses existing ruled-ledger, labeled-bar, table, responsive-summary, focus, and motion patterns.

#### Fixed

- Corrected the Analytics focus audit to inspect the deliberately focused segment selector.
- Added lower-page captures so prediction-outcome and segment content are visually inspected at mobile and desktop widths.

#### Verified

- Python compilation passed.
- Full suite passed: 90 tests.
- All 75 previously accepted tests remained passing.
- Browser QA passed: 49 captured states.
- Analytics summary remained deterministic: 4 predictions, 52.75% average risk, 50% High-risk rate, and Low 1 / Medium 1 / High 2.
- Existing fixture outputs remained unchanged.
- All six routes passed with zero application console/page errors, zero horizontal overflow, zero visible unnamed controls, visible keyboard focus, and reduced-motion support.
- Anti-Slop review passed with no fabricated metrics or generic BI-dashboard treatment.

## [0.5.0] — 2026-10-05

### Vertical Slice 5 — Batch Prediction

Feature checkpoint: `539a098 — feat: prove churnguard batch prediction slice`

Acceptance-documentation checkpoint: `7e0c8c6 — docs: record batch prediction acceptance`

#### Added

- Added `/app/batch` as a routed Batch Prediction workspace.
- Added Batch Prediction to the established ChurnGuard command rail and application router.
- Added a Batch header with:
  - concise operational purpose;
  - deterministic frontend-demo disclosure;
  - explicit absence of a backend, trained model, production activity, and model-performance metrics.
- Added typed Batch architecture:
  - `BatchService` protocol;
  - safe `BatchServiceError`;
  - `BatchValidationIssue`;
  - `BatchValidationResult`;
  - `BatchSummary`;
  - `BatchResult`;
  - deterministic `MockBatchService`;
  - typed demo-state modes.
- Added an approved four-customer demo batch generated directly from the existing fixtures.
- Added deterministic input CSV and results CSV generation without introducing a second data source.
- Added two supported input paths:
  - load the approved deterministic demo batch;
  - upload a UTF-8 CSV.
- Added downloadable approved input CSV and CSV template actions.
- Added visible CSV schema requirements using all existing `CustomerInput` aliases.
- Added native file upload restricted to CSV.
- Added UTF-8 decoding and strict CSV parsing.
- Added schema validation for required columns.
- Added typed row validation through the existing `CustomerInput` model.
- Added canonical fixture matching that rejects:
  - unknown customers;
  - edited fixture values;
  - missing required values;
  - unsupported typed values.
- Added a compact dataset preview containing:
  - customer ID;
  - tenure;
  - contract;
  - monthly charges.
- Added validation summaries for:
  - total records;
  - valid records;
  - invalid records;
  - source filename;
  - validation status.
- Added row-level validation reports with row number, customer identifier where available, and actionable copy.
- Added intentional workflow states:
  - initial / no dataset;
  - dataset selected;
  - fully valid dataset;
  - invalid row;
  - empty header-only dataset;
  - malformed non-UTF-8 input;
  - uploaded approved CSV;
  - immediate processing spinner;
  - successful results;
  - recoverable service error;
  - retry with preserved validated data.
- Added one clear Run Batch Analysis action that remains disabled when validation blocks processing.
- Added deterministic orchestration through the existing `MockPredictionService` rather than duplicating prediction logic.
- Added a connected result ledger showing only calculated batch values:
  - records analyzed;
  - High-risk count;
  - Medium / Watch count;
  - Low-risk count;
  - average predicted risk.
- Added a direct-count risk distribution with textual High, Medium / Watch, and Low labels plus restrained bars.
- Added probability-first deterministic prioritization with customer-ID tie-breaking.
- Added a semantic six-column desktop results table containing:
  - customer ID;
  - predicted probability;
  - textual risk;
  - top driver;
  - tenure;
  - contract.
- Added deliberate mobile and tablet summaries preserving:
  - customer identity;
  - textual risk;
  - probability;
  - top driver;
  - tenure;
  - contract.
- Added four named native inspection actions for analyzed customers.
- Added Batch → Customer Detail navigation using the accepted:
  - `/app/customer-detail?fixture={customerId}` contract.
- Added deterministic results CSV export containing only fixture-backed result fields.
- Added reusable shared `StreamlitPage` route objects.
- Added 19 Batch tests covering:
  - idle state;
  - valid deterministic validation;
  - invalid row reporting;
  - empty input;
  - malformed input;
  - missing schema columns;
  - approved uploaded CSV;
  - edited-row rejection;
  - summary calculations;
  - risk distribution counts;
  - priority ordering;
  - unchanged fixture predictions;
  - invalid/empty run prevention;
  - recoverable service failure and retry;
  - deterministic result export;
  - successful page flow;
  - page validation states;
  - page error/retry;
  - selected fixture preservation for inspection.
- Expanded browser QA to 40 captured states.
- Added reusable Batch workflow rules to `design-system/DESIGN.md`.
- Added `docs/BATCH_ACCEPTANCE_EVIDENCE.md`.

#### Changed

- Centralized all accepted route definitions in `frontend/streamlit_app/routes.py`.
- Updated Customer Detail to accept a fixture selected through native internal Batch navigation and restore the canonical query parameter.
- Updated the canonical flow to:
  - Batch Prediction;
  - inspect analyzed customer;
  - Customer Detail;
  - existing Prediction Workspace.
- Updated `README.md` with:
  - `/app/batch`;
  - supported input behavior;
  - typed Batch boundary;
  - frontend-only limitations.
- Updated `docs/ARCHITECTURE.md` with:
  - Batch service ownership;
  - validation flow;
  - deterministic prediction composition;
  - result flow;
  - native Customer Detail navigation.
- Expanded browser QA to verify:
  - successful Batch results at 375, 768, 1024, and 1440px;
  - mobile priority summaries and inspection controls;
  - initial state;
  - valid validation;
  - invalid, empty, and malformed datasets;
  - native CSV upload;
  - recoverable service error and retry;
  - Batch → Customer Detail navigation;
  - Customer Detail, Customer History, Customer Analysis, and Command Center regressions;
  - semantic structures;
  - keyboard focus;
  - reduced motion;
  - visible control naming;
  - horizontal overflow;
  - console, page, and HTTP errors.
- Hardened browser monitoring so newly opened inspection pages are audited as well as directly created pages.
- Preserved the current Streamlit version and frontend-only architecture.

#### Fixed

- Normalized CSV `SeniorCitizen` string values `"0"` and `"1"` into the existing integer literal contract before typed validation.
- Corrected responsive browser assertions that initially targeted hidden desktop or mobile duplicate records.
- Made visual-QA validation helpers wait for each intended valid, invalid, empty, or malformed outcome.
- Corrected upload QA to target Streamlit’s underlying native file input instead of the presentational drop zone.
- Restored isolated browser contexts per state so mobile sidebar state could not leak into desktop checks.
- Corrected primary Streamlit button text from muted body color to accessible white against the amber action background.
- Replaced raw Batch inspection links with native Streamlit page switching.
- Preserved the selected fixture through session state and restored the canonical Customer Detail query parameter.
- Eliminated the first-navigation Streamlit route-fallback dialog from the Batch inspection flow.
- Corrected the shared route registry to use absolute page paths so direct page tests and the application router resolve the same files.
- Moved page switching from a callback into the button event body so navigation executes reliably.

#### Verified

- Python compilation passed.
- Full automated suite passed: 75 tests.
- All 56 previously accepted tests remained passing.
- Browser QA passed for 40 captured states.
- Responsive verification passed at 375, 768, 1024, and 1440px.
- Deterministic Batch results were confirmed:
  - 4 records analyzed;
  - 2 High;
  - 1 Medium / Watch;
  - 1 Low;
  - 52.75% average predicted risk.
- Priority order was confirmed:
  1. `CUST-HIGH-001` — 87%, High.
  2. `CUST-HARD-001` — 61%, High.
  3. `CUST-BORDERLINE-001` — 52%, Medium / Review.
  4. `CUST-LOW-001` — 11%, Low.
- Existing fixture outputs remained unchanged:
  - `CUST-LOW-001` — 11%, Low;
  - `CUST-HIGH-001` — 87%, High;
  - `CUST-BORDERLINE-001` — 52%, Medium / Review;
  - `CUST-HARD-001` — 61%, High and review-worthy.
- Browser audit reported:
  - 0 application console/page errors;
  - 0 horizontal-overflow findings;
  - 0 visible unnamed interactive controls;
  - 1 logical H1;
  - 1 semantic Batch results table;
  - 6 result column headers;
  - 5 summary values;
  - 3 labeled distribution rows;
  - 4 named customer inspection actions;
  - visible keyboard focus;
  - reduced-motion support.
- Accessibility verification passed:
  - visible source and upload labels;
  - keyboard-operable native controls;
  - meaningful validation status and errors;
  - semantic preview and results tables;
  - risk communicated through words, symbols, probabilities, counts, and color;
  - sufficient primary-action contrast;
  - appropriate touch targets;
  - customer-specific action names.
- Anti-Slop review passed:
  - no generic upload-dashboard treatment;
  - no giant upload illustration;
  - no floating KPI-card grid;
  - no decorative charts;
  - no gradients or glassmorphism;
  - no fake metrics, model claims, activity, or production volume;
  - no sparkle imagery or unnecessary animation.
- Runtime verification passed for:
  - `/app`;
  - `/app/predict`;
  - `/app/customers`;
  - `/app/customer-detail?fixture={customerId}`;
  - `/app/batch`.
- Batch → Customer Detail navigation was verified without a route-fallback error.
- No fabricated customer data, predictions, timestamps, metrics, SHAP values, or production activity were introduced.

#### Intentional limitations

- Uploaded rows must exactly match approved deterministic fixtures in this frontend-only stage.
- Invalid batches are blocked rather than partially scored.
- Processing is immediate and local; no production-scale duration or progress estimate is implied.
- Results are not persisted after the Streamlit session.
- All results use the fixed fixture timestamp and demo model version.
- Backend batch APIs, arbitrary-customer inference, production-scale upload handling, and later product slices remain deferred.

## [0.4.0] — 2026-10-05

### Vertical Slice 4 — Customer Detail

Feature checkpoint: `93ad934 — feat: prove churnguard customer detail slice`

Acceptance-documentation checkpoint: `fea0f64 — docs: record customer detail acceptance`

#### Added

- Added `/app/customer-detail?fixture={customerId}` as the approved Streamlit-compatible Customer Detail route.
- Added Customer Detail to the existing `st.navigation` router and ChurnGuard application shell.
- Added safe resolution and validation of the `fixture` query parameter.
- Added typed Customer Detail architecture:
  - `CustomerDetailResult`;
  - `MockCustomerDetailService`;
  - `CustomerDetailNotFound`;
  - `CustomerDetailDataError`;
  - typed fixture and malformed-data modes.
- Added a customer header containing only fixture-backed information:
  - customer ID;
  - contract;
  - tenure;
  - internet service;
  - textual risk state;
  - churn probability;
  - fixed prediction timestamp;
  - approved-demo status.
- Added a prominent risk brief with:
  - churn probability;
  - explicit risk classification;
  - operating threshold;
  - labeled probability meter;
  - fixture-specific interpretation;
  - hard-case review wording.
- Added a ranked three-driver ledger showing:
  - driver rank;
  - fixture driver name;
  - raises/lowers-risk direction;
  - signed fixture contribution;
  - exact deterministic explanation;
  - directly supported customer value where available.
- Added driver-value mapping only for fields present in the fixture:
  - contract;
  - tenure;
  - monthly charges;
  - payment method;
  - device protection.
- Added a customer-specific plain-English explanation using the existing fixture scenario and explanation copy.
- Added explicit caveat text distinguishing deterministic fixture evidence from causal or real-model explanations.
- Added the existing deterministic retention recommendation with:
  - priority;
  - summary;
  - operational action list;
  - decision-support caveat.
- Added grouped fixture context using ruled definition lists:
  - Customer;
  - Account;
  - Services.
- Added prediction context for:
  - prediction ID;
  - fixed timestamp;
  - operating threshold;
  - demo model version;
  - deterministic JSON source;
  - fixture-service status.
- Added named navigation actions:
  - Back to Customer History;
  - Open selected customer in Prediction Workspace;
  - Command Center.
- Added intentional Customer Detail states:
  - valid fixture;
  - missing fixture;
  - unknown fixture;
  - malformed fixture value;
  - recoverable malformed-data/service state;
  - synchronous loading feedback without artificial delay.
- Added approved behavior for:
  - `CUST-LOW-001`;
  - `CUST-HIGH-001`;
  - `CUST-BORDERLINE-001`;
  - `CUST-HARD-001`.
- Added 16 Customer Detail tests covering:
  - all four deterministic outputs;
  - fixture-backed driver context;
  - customer identity;
  - risk;
  - drivers;
  - explanation;
  - recommendation;
  - customer/account/service context;
  - prediction metadata;
  - missing, unknown, malformed, and recoverable-error states;
  - Customer History and Prediction Workspace navigation contracts.
- Expanded browser QA to 27 captured states covering Customer Detail and all accepted regressions.
- Added a reusable Customer Detail hierarchy to `design-system/DESIGN.md`.
- Added `docs/CUSTOMER_DETAIL_ACCEPTANCE_EVIDENCE.md`.

#### Changed

- Updated Customer History inspection actions to open Customer Detail before Prediction Workspace.
- Updated the canonical operational flow to:
  - Command Center;
  - Customer History;
  - Customer Detail;
  - Prediction Workspace.
- Updated `README.md` with the Customer Detail scope, route, architecture, and fixture-only limitation.
- Updated `docs/ARCHITECTURE.md` with:
  - Customer Detail service ownership;
  - query-parameter validation;
  - fixture-to-prediction flow;
  - the current Streamlit routing decision.
- Documented that `/app/customer-detail?fixture={customerId}` is used because Streamlit 1.50 does not support nested dynamic `/app/customers/[id]` page routes.
- Preserved the existing Streamlit version and application architecture without adding:
  - another frontend framework;
  - proxy routing;
  - custom URL rewriting;
  - backend routing;
  - a second prediction system.
- Expanded browser QA to verify:
  - Customer Detail at 375, 768, 1024, and 1440px;
  - mobile risk and driver hierarchy;
  - desktop grouped customer context;
  - low-risk, high-risk, borderline, and hard-case records;
  - missing, unknown, and recoverable-error states;
  - Customer History → Customer Detail navigation;
  - Customer Detail → Prediction Workspace navigation;
  - accepted 87% High prediction after handoff;
  - Command Center regression;
  - Customer History regression;
  - semantic structure;
  - keyboard focus;
  - reduced motion;
  - visible control naming;
  - horizontal overflow;
  - application console/page errors.

#### Fixed

- Replaced direct Customer History → Prediction Workspace inspection links with the approved Customer History → Customer Detail → Prediction Workspace flow.
- Safely rejected malformed fixture values without rendering unsafe input or crashing the page.
- Added explicit missing and unknown fixture recovery instead of allowing invalid customer requests to fall through.
- Preserved fixture IDs through the Customer Detail-to-Prediction Workspace handoff.
- Extended the browser audit to separate known Streamlit nested-route bootstrap probes from genuine application console, page, and HTTP failures.
- Re-ran browser QA after a transient Streamlit route-fallback warning; the complete repeat pass reported zero application errors.

#### Verified

- Python compilation passed.
- Full automated suite passed: 56 tests.
- All 40 previously accepted tests remained passing.
- Deterministic fixture outputs remained unchanged:
  - `CUST-LOW-001` — 11%, Low;
  - `CUST-HIGH-001` — 87%, High;
  - `CUST-BORDERLINE-001` — 52%, Medium / Review;
  - `CUST-HARD-001` — 61%, High and review-worthy.
- Browser QA passed for 27 captured states.
- Responsive verification passed at 375, 768, 1024, and 1440px.
- Browser audit reported:
  - 0 application console/page errors;
  - 0 horizontal-overflow findings;
  - 0 visible unnamed interactive controls;
  - 1 logical H1;
  - 1 ordered driver list;
  - 3 driver records;
  - 3 labeled customer-context sections;
  - visible keyboard focus;
  - reduced-motion support.
- Accessibility verification passed:
  - semantic heading hierarchy;
  - meaningful customer-specific navigation names;
  - keyboard-operable controls;
  - visible focus;
  - grouped definition-list context;
  - risk communicated by percentage, label, symbol, copy, and color;
  - meaningful missing, unknown, malformed, and error recovery.
- Anti-Slop review passed:
  - no generic CRM profile or avatar card;
  - no floating KPI-card grid;
  - no decorative charts;
  - no gradients or glassmorphism;
  - no fake activity, testimonials, model metrics, or production claims;
  - no excessive pills, icons, or animation.
- Runtime verification passed for:
  - `/app`;
  - `/app/predict`;
  - `/app/customers`;
  - `/app/customer-detail?fixture={customerId}`.
- Command Center, Customer Analysis, and Customer History remained regression-free.
- Customer History → Customer Detail → Prediction Workspace was verified end to end.
- No fabricated customer data, predictions, SHAP values, timestamps, model-performance claims, or production activity were introduced.

#### Intentional limitations

- Customer Detail supports only the four approved deterministic fixtures.
- The current Streamlit frontend uses the approved `fixture` query parameter rather than a nested dynamic route.
- All fixtures share one fixed demo timestamp, so no customer risk timeline is available.
- Recommendations are deterministic decision-support fixtures and are not claims of proven churn reduction.
- Persistence, production data, backend APIs, real inference, authentication, and later product slices remain deferred.

## [0.3.0] — 2026-10-05

### Vertical Slice 3 — Customer History

Source checkpoint: `94bfc4 — docs: add complete project changelog`

Feature checkpoint: `6d941e8 — feat: prove churnguard customer history slice`

Acceptance-documentation checkpoint: `2c20184 — docs: record customer history acceptance checkpoint`

#### Added

- Added `/app/customers` as a routed Customer History workspace.
- Added Customer History to the established ChurnGuard command rail and application router.
- Added a Customer History header with:
  - concise operational purpose;
  - explicit deterministic-demo disclosure;
  - fixture-service state;
  - demo model version;
  - fixed fixture-snapshot timestamp.
- Added typed Customer History architecture:
  - `CustomerHistoryQuery`;
  - `CustomerHistoryResult`;
  - `MockCustomerHistoryService`;
  - safe `CustomerHistoryDataError`;
  - typed history mode, tenure-bucket, and sort contracts.
- Added fixture-backed search across:
  - customer ID;
  - top driver;
  - contract;
  - scenario.
- Added a named Clear action and complete search/filter reset behavior.
- Added risk filters for:
  - All;
  - Low;
  - Watch / Medium;
  - High.
- Added contract options derived exclusively from the supplied fixture values:
  - Month-to-month;
  - One year;
  - Two year.
- Added deterministic tenure buckets:
  - 0–12 months;
  - 13–36 months;
  - 37+ months.
- Added prediction-date filtering using only the authoritative fixed fixture timestamp.
- Added deterministic operational sorting:
  - highest risk first;
  - lowest risk first;
  - newest prediction;
  - oldest prediction;
  - customer ID as a stable tie-breaker.
- Added combined search and filter behavior at the typed service boundary rather than in arbitrary rendering code.
- Added a semantic nine-column desktop history table containing:
  - customer ID;
  - churn probability;
  - textual risk;
  - top driver;
  - tenure;
  - contract;
  - prediction timestamp;
  - model version;
  - named inspection action.
- Added deliberate mobile and tablet record summaries that preserve:
  - customer identity;
  - textual risk;
  - churn probability;
  - top driver;
  - inspection action;
  - expandable supporting metadata.
- Added distinct populated, empty-history, search-empty, filter-empty, and recoverable malformed-history states.
- Added direct inspection actions that open the selected fixture in the accepted `/app/predict` workflow without duplicating prediction logic.
- Added Customer History-specific responsive and density rules to `design-system/DESIGN.md`.
- Added `docs/CUSTOMER_HISTORY_ACCEPTANCE_EVIDENCE.md`.
- Added 16 deterministic Customer History tests covering:
  - history loading;
  - all four fixture records;
  - search and no-match search;
  - risk, contract, tenure, and date filters;
  - deterministic sorting;
  - combined filters;
  - empty and malformed data contracts;
  - semantic history rendering;
  - search-empty and filter-empty UI;
  - reset behavior;
  - inspection-link contracts;
  - selected-customer handoff into `/app/predict`.
- Expanded browser QA to capture 14 important rendered states.

#### Changed

- Updated `README.md` with the Customer History route, scope, architecture, and current limitations.
- Updated `docs/ARCHITECTURE.md` with the Customer History service flow and ownership boundary.
- Updated the shared application shell so every routed page receives the established ChurnGuard design system reliably.
- Hid Streamlit’s generated route navigation so the ChurnGuard command rail remains the sole visible application navigation.
- Expanded the browser audit to verify:
  - populated history at 375, 768, 1024, and 1440px;
  - intentional responsive record presentation;
  - search and clear behavior;
  - individual and combined filters;
  - fixture-date selection;
  - sorting;
  - search-empty and filter-empty states;
  - empty-history and recoverable-error states;
  - customer inspection navigation;
  - accepted prediction-workflow regression;
  - Command Center regression;
  - semantic structure;
  - keyboard focus;
  - reduced motion;
  - visible control naming;
  - horizontal overflow;
  - application console/page errors.

#### Fixed

- Fixed the desktop table contributing hidden width at mobile breakpoints when routed pages did not reliably receive the shared stylesheet.
- Fixed duplicate generic Streamlit navigation appearing above the established ChurnGuard command rail.
- Fixed browser-QA targeting of hidden desktop table duplicates on mobile.
- Fixed browser-QA select targeting to use Streamlit’s generated accessible names safely.
- Separated known Streamlit nested-route bootstrap probes from genuine application console, page, and HTTP errors in the QA report.
- Preserved all existing Command Center and Customer Analysis behavior.

#### Verified

- Python compilation passed.
- Full automated suite passed: 40 tests.
- All 24 previously accepted tests remained passing.
- Browser QA passed for 14 captured states.
- Responsive verification passed at 375, 768, 1024, and 1440px.
- Browser audit reported:
  - 0 application console/page errors;
  - 0 horizontal-overflow findings;
  - 0 visible unnamed interactive controls;
  - 1 logical H1;
  - 1 semantic history table;
  - 9 table column headers;
  - visible keyboard focus;
  - reduced-motion support.
- Accessibility verification passed:
  - semantic headings;
  - accessible search and filters;
  - keyboard-operable controls;
  - meaningful inspection names;
  - risk communicated through words and symbols as well as color;
  - clear empty and error recovery.
- Anti-Slop review passed:
  - no generic dashboard card grid;
  - no decorative charts;
  - no gradients or glassmorphism;
  - no ornamental illustrations;
  - no fake activity, volume, or model metrics.
- Runtime verification passed for `/app`, `/app/predict`, and `/app/customers`.
- Customer History inspection successfully loaded `CUST-HIGH-001` in `/app/predict` and reproduced the accepted 87% High result.
- Existing deterministic fixture regressions remained unchanged:
  - `CUST-LOW-001` — 11%, Low;
  - `CUST-HIGH-001` — 87%, High;
  - `CUST-BORDERLINE-001` — 52%, Medium / Review;
  - `CUST-HARD-001` — 61%, High and review-worthy.
- No fabricated customers, predictions, timestamps, model versions, metrics, or production activity were introduced.

#### Intentional limitations

- Customer History contains only the four approved deterministic fixtures.
- All fixtures share the one authoritative fixed prediction timestamp; newest/oldest ties resolve by customer ID.
- Pagination and export were not added because neither is justified for four approved records.
- Persistence, production data, backend APIs, real inference, authentication, and Customer Detail remain deferred.

## [0.2.0] — 2026-10-04

### Vertical Slice 2 — Command Center

Git checkpoint: `b882bb2 — feat: prove churnguard command center slice`

#### Added

- Added the Streamlit Command Center at `/app`.
- Added explicit routed views:
  - `/app` for the Command Center.
  - `/app/predict` for the accepted customer-analysis workflow.
- Added `.streamlit/config.toml` with the `/app` base path and the established ChurnGuard theme tokens.
- Added primary navigation between Command Center and Analyze Customer while preserving the existing application shell.
- Added a typed `MockCommandCenterService` that composes the existing prediction service instead of duplicating fixture calculations in the UI.
- Added typed Command Center models for:
  - prediction-history rows;
  - KPI summaries;
  - risk distribution;
  - review items;
  - complete Command Center snapshots.
- Added a Command Center header with:
  - operational context;
  - deterministic demo-model version;
  - fixture-service status;
  - fixed snapshot timestamp.
- Added a connected operational KPI ledger showing values derived exclusively from the four approved fixtures:
  - 4 predictions analyzed;
  - 2 high-risk customers;
  - 52.75% average predicted risk;
  - 50% high-risk share.
- Added a deterministic priority queue with:
  - customer ID;
  - churn probability;
  - risk label;
  - top driver;
  - tenure;
  - contract;
  - fixture timestamp;
  - named customer-inspection action.
- Added priority ordering by risk band and descending probability:
  1. `CUST-HIGH-001` — 87%, High.
  2. `CUST-HARD-001` — 61%, High.
  3. `CUST-BORDERLINE-001` — 52%, Medium/Watch.
  4. `CUST-LOW-001` — 11%, Low.
- Added customer inspection links that open the selected fixture in `/app/predict`.
- Added a direct-count risk distribution:
  - Low: 1;
  - Medium/Watch: 1;
  - High: 2;
  - operating threshold: 50% from the fixture contract.
- Added a compact recent-activity ledger that explicitly identifies itself as one fixed fixture snapshot rather than live production history.
- Added an honest pre-ML model-health summary with:
  - deterministic JSON fixture source;
  - demo fixture version;
  - mock-service inference state;
  - production API not connected;
  - model evaluation pending.
- Added a Needs Review register for:
  - the borderline prediction;
  - the conflicting-signal hard case;
  - the supplied incomplete-input test state;
  - the supplied recoverable service-error test state.
- Added deterministic Command Center state controls for:
  - sample snapshot;
  - empty history;
  - malformed history.
- Added a purposeful empty state with a direct path to Analyze Customer.
- Added a safe malformed-snapshot error state with retry guidance and no internal error leakage.
- Added Command Center-specific design rules to `design-system/DESIGN.md`.
- Added `docs/COMMAND_CENTER_ACCEPTANCE_EVIDENCE.md`.
- Added reproducible browser-QA metadata and the `visual:qa` npm script in `package.json`.
- Added seven deterministic Command Center tests covering:
  - snapshot calculations;
  - risk distribution;
  - priority ordering;
  - empty history;
  - malformed history;
  - page rendering and inspect-link contract;
  - empty and error UI states.

#### Changed

- Refactored the original single-page Streamlit entry point into a small router using `st.navigation`.
- Moved the accepted prediction experience into `frontend/streamlit_app/pages/predict.py`.
- Updated the prediction view to load a fixture supplied by a Command Center inspection URL.
- Expanded the application shell from one active item to Command Center and Analyze Customer navigation.
- Updated the responsive system for dense operational queue rows:
  - ruled eight-column ledger on large screens;
  - labeled records at tablet and mobile widths;
  - no horizontal page overflow.
- Updated `README.md` with both routes, Command Center scope, architecture, setup, and browser-QA instructions.
- Updated `docs/ARCHITECTURE.md` with routed page flow and Command Center service ownership.
- Expanded browser QA to verify:
  - Command Center at 375, 768, 1024, and 1440px;
  - mobile priority queue;
  - lower distribution, review, activity, and model-health sections;
  - empty state;
  - malformed-data state;
  - customer inspection navigation;
  - accepted prediction workflow regression.
- Increased the full automated test suite from 17 to 24 tests.
- Added `node_modules/` to `.gitignore`.

#### Fixed

- Moved development-only state controls from the top of the operational page into the command rail so they no longer interrupt the page hierarchy.
- Corrected sidebar select text contrast against its light control surface.
- Preserved readable risk meaning through text labels and symbols in addition to semantic colors.
- Ensured queue records reflow without clipping or horizontal page scroll.
- Ensured all visible interactive controls have accessible names.
- Confirmed customer inspect actions load the intended fixture in the accepted prediction workflow.

#### Verified

- Python compilation passed.
- Full automated suite passed: 24 tests.
- All 17 accepted Vertical Slice 1 tests continued to pass.
- Streamlit started successfully with both routed views.
- Browser QA passed with 11 screenshots.
- Responsive verification passed at 375, 768, 1024, and 1440px.
- Browser audit reported:
  - 0 console/page errors;
  - 0 horizontal-overflow findings;
  - 0 visible unnamed interactive controls;
  - 1 semantic priority-queue table;
  - 6 named customer-inspection links.
- Anti-Slop review passed:
  - no fabricated customers;
  - no fake activity or model metrics;
  - no floating generic KPI-card grid;
  - no decorative charts, gradients, glassmorphism, or AI imagery.

## [0.1.0] — 2026-10-04

### Vertical Slice 1 — Customer Analysis

Git checkpoint: `5d7f34d — feat: prove churnguard customer analysis slice`

#### Project foundation

- Recorded the supplied project authority files:
  - `MASTER-WEB-DEV-WORKFLOW.md`;
  - `ChurnGuard_Master_JSON_Prompt.json`;
  - `CHURNGUARD_FRONTEND_BUILD_SPEC.md`;
  - `CHURNGUARD_SAMPLE_DATA.json`;
  - `CHURNGUARD_FRONTEND_ACCEPTANCE_CHECKLIST.md`.
- Recorded all mandatory design references under `Design Reference/`.
- Established a Python and Streamlit project structure.
- Added pinned Python dependencies for Streamlit, Pydantic, and pytest.
- Added pytest configuration and Python package markers.
- Added `.gitignore` coverage for virtual environments, secrets, caches, build output, and QA artifacts.

#### Design system

- Created `design-system/DESIGN.md` as the ChurnGuard visual source of truth.
- Established the Retention Control Room identity:
  - dark navy command rail;
  - mineral canvas;
  - warm operational accent;
  - semantic low, watch, high, and error colors;
  - fine rules and compact operational labels;
  - tabular numeric treatment.
- Defined typography, spacing, sizing, borders, radii, elevation, focus, motion, state, density, chart, and responsive rules.
- Added risk-visualization and driver-explanation rules.
- Added explicit Anti-Slop constraints against fabricated metrics, generic dashboards, gradients, glassmorphism, excessive cards, sparkle imagery, and decorative charts.

#### Architecture and data

- Added typed Pydantic models for:
  - customer input;
  - prediction request;
  - prediction response;
  - risk labels;
  - signed drivers;
  - recommendations;
  - service capabilities.
- Added a replaceable `PredictionService` protocol.
- Added a deterministic `MockPredictionService`.
- Centralized all fixture lookup, deterministic prediction mapping, latency simulation, and one-shot failure behavior in the service layer.
- Loaded `CHURNGUARD_SAMPLE_DATA.json` directly as the only prediction source.
- Explicitly rejected edited values that do not match an approved fixture instead of inventing inference.
- Documented the future mock-to-HTTP/FastAPI replacement boundary.
- Explicitly documented that production authentication is deferred and not simulated as implemented.

#### Customer-analysis experience

- Added the complete accepted workflow:
  - select a sample customer;
  - load the form;
  - validate input;
  - submit through the prediction-service boundary;
  - show loading;
  - show risk probability and label;
  - show operating threshold;
  - show three ranked signed drivers;
  - show deterministic plain-English explanations;
  - show recommended retention action.
- Added customer profile, account, and service field groups.
- Added four approved sample options:
  - `CUST-LOW-001`;
  - `CUST-HIGH-001`;
  - `CUST-BORDERLINE-001`;
  - `CUST-HARD-001`.
- Added honest demo-data labeling and disclaimers.
- Added a probability meter with an explicit 50% threshold marker.
- Added Low, Review, and High states using labels, symbols, copy, and color.
- Added hard-case wording for conflicting risk and retention signals.
- Added ranked driver direction, signed impact, and explanation presentation.
- Added customer snapshot and fixture-version context.
- Added edit-and-rerun behavior.

#### States and validation

- Added idle, loading, success, validation-error, service-error, retry, empty, and disabled states.
- Added field-specific inline validation.
- Added validation for:
  - required values;
  - missing customer ID;
  - missing fields;
  - numeric parsing;
  - numeric ranges;
  - unsupported categories.
- Preserved user input after recoverable failures.
- Added a development-only one-shot service failure control.
- Added a recoverable error message that does not expose implementation details.
- Added retry with preserved validated customer input.

#### Responsive and accessibility work

- Added a persistent command rail for large desktops.
- Added a compact product identity for tablet and mobile.
- Added deliberate layouts for 375, 768, 1024, and 1440px.
- Added single-column mobile form and result flow.
- Added tablet stacking where the split layout became cramped.
- Added visible focus treatment.
- Added minimum target sizing for primary controls.
- Added logical heading structure and visible native labels.
- Added non-color-only risk communication.
- Added reduced-motion behavior.
- Verified WCAG AA token contrast and darkened accent/watch colors where needed.

#### Defects fixed during proof

- Fixed the expanded mobile sidebar intercepting form controls.
- Fixed cramped and truncated layouts at 768px and 1024px.
- Fixed fixture selection not refreshing Streamlit widget state.
- Reworked fixture loading into a state-safe callback.
- Replaced an overemphasized red retry button with a restrained secondary action.
- Replaced unnamed numeric stepper controls with labeled numeric text entry and typed validation.
- Moved validation feedback from a detached form summary to field-specific inline messages.
- Fixed small-text contrast for accent and watch colors.
- Corrected submit-button text contrast.

#### Tests and verification

- Added deterministic validation tests.
- Added mock-service tests for all four fixtures.
- Added a known high-risk input/output regression test.
- Added tests for edited-input rejection.
- Added service failure and retry recovery tests.
- Added explicit authentication-deferral contract coverage.
- Added Streamlit app tests for:
  - idle state;
  - sample selection;
  - successful prediction;
  - result content;
  - invalid input;
  - service failure;
  - retry.
- Added browser-based visual QA for:
  - idle;
  - loading;
  - validation;
  - service error;
  - retry success;
  - low risk;
  - high risk;
  - borderline;
  - hard case;
  - all four responsive widths.
- Verified:
  - 17 passing tests;
  - successful Python compilation;
  - successful Streamlit startup;
  - zero browser console/page errors;
  - zero horizontal-overflow findings;
  - zero visible unnamed interactive controls;
  - no committed secrets or real customer PII.

#### Documentation

- Added project setup, run, test, architecture, fixture usage, and limitation guidance to `README.md`.
- Added `docs/ARCHITECTURE.md`.
- Added `docs/FRONTEND_ACCEPTANCE_EVIDENCE.md`.
- Recorded the first proven Git checkpoint.

### Explicitly not implemented

The following remain intentionally deferred:

- FastAPI;
- real model inference;
- Logistic Regression, Random Forest, or XGBoost training;
- real SHAP computation;
- model calibration;
- MLflow;
- persistence/database infrastructure;
- production authentication;
- production monitoring;
- deployment.