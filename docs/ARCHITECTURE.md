# Frontend architecture

## Decision

Use Streamlit because it is the required capstone frontend and is sufficient for the current operator workflow. Use Pydantic models at the application boundary and a `PredictionService` protocol so the UI is independent of fixture and transport details.

## Current flow

```text
app.py router
  ├── /app → Command Center page
  │     → MockCommandCenterService
  │     → MockPredictionService
  │     → deterministic operational snapshot
  ├── /app/predict → customer-analysis page
        → validation.py
        → PredictionRequest
        → PredictionService
        → MockPredictionService
        → PredictionResponse
        → presentation components
  ├── /app/customers → Customer History page
        → CustomerHistoryQuery
        → MockCustomerHistoryService
        → MockPredictionService
        → deterministic filtered/sorted history
        → semantic table or responsive record summaries
  ├── /app/customer-detail?fixture={customerId} → Customer Detail page
        → fixture query-parameter validation
        → MockCustomerDetailService
        → MockPredictionService
        → CustomerDetailResult
        → risk, drivers, recommendation, fixture context, metadata
  └── /app/batch → Batch Prediction page
        → BatchService contract
        → MockBatchService
        → schema and row validation
        → MockPredictionService for each approved fixture
        → BatchResult summary and priority ordering
        → Customer Detail inspection
  └── /app/analytics → Analytics page
        → AnalyticsService contract
        → MockAnalyticsService
        → MockPredictionService
        → deterministic AnalyticsSnapshot
        → direct-count distributions, one-date volume, and segment ledger
  └── /app/model → Model Intelligence / Model Status page
        → ModelService contract
        → MockModelService
        → MockPredictionService fixture contract
        + ChurnGuard_Master_JSON_Prompt.json pipeline requirements
        → deterministic ModelSnapshot
        → current status, metadata availability, threshold context, and candidate ledger
  └── /app/model-explanations?fixture={customerId} → Model Explanations page
        → ExplanationService contract
        → MockExplanationService
        ├── MockPredictionService
        └── MockCustomerDetailService
        → CHURNGUARD_SAMPLE_DATA.json explanation fixtures
        → global demo ranking and local operational explanation
```

## Future flow

```text
Streamlit UI
  → HttpPredictionService
  → FastAPI POST /predict
  → model pipeline and explainability
```

The HTTP implementation will own credentials, status-code mapping, timeouts, and transport errors. Authentication is not implemented or simulated as production behavior in this frontend stage.

The Command Center service composes the prediction service rather than duplicating fixture calculations in the page. It owns KPI derivation, risk-band counts, priority ordering, review-state mapping, and empty/malformed snapshot behavior.

The Customer History service also composes the prediction service. It owns fixture-row construction, case-insensitive search, risk/contract/tenure/date filtering, deterministic sorting, and empty/malformed history behavior. The page owns only control state and presentation. Selecting a row routes the fixture identifier into Customer Detail, which provides the next action into `/app/predict`.

Customer Detail uses `/app/customer-detail?fixture={customerId}` because the current Streamlit 1.50 router does not support nested dynamic `/app/customers/[id]` paths. No proxy, URL rewrite, framework change, or alternate prediction system was introduced. This is a routing constraint of the current Streamlit frontend implementation, not a general production limitation of ChurnGuard.

Customer History passes the selected deterministic fixture to Customer Detail. `MockCustomerDetailService` resolves the customer and calls the existing `MockPredictionService`; the page does not calculate or duplicate predictions. Customer Detail can then pass the same fixture to `/app/predict`.

Batch uses a typed `BatchService` boundary. `MockBatchService` owns CSV generation, UTF-8/schema/row validation, canonical fixture matching, deterministic analysis, summary calculations, priority ordering, and CSV export. The page owns only source selection, upload state, actions, and presentation.

The deterministic demo path is built directly from all four approved fixtures. Uploaded rows must use the existing `CustomerInput` schema and exactly match an approved fixture; arbitrary uploaded values do not produce invented predictions.

Batch customer inspection uses native Streamlit page switching through shared `StreamlitPage` route objects. The selected fixture is preserved in session state, and Customer Detail writes the canonical `fixture` query parameter. This avoids a first-navigation route fallback while preserving the accepted `/app/customer-detail?fixture={customerId}` contract.

Analytics uses a typed `AnalyticsService` boundary. `MockAnalyticsService` composes the existing prediction service and owns all calculations: fixture volume by supplied date, Low/Medium/High counts, average predicted risk, High-risk rate, supported segment grouping, average segment risk, High counts, High shares, deterministic ordering, and the concise highest-average segment interpretation.

The Analytics UI owns only the selected authoritative segment, demo-state control, and presentation. Supported segments are limited to contract, the existing 0–12 / 13–36 / 37+ tenure buckets, internet service, and payment method because those values exist in the approved customer fixtures.

The approved source does not contain prediction-attempt outcomes. The Analytics contract therefore reports success/failure availability as false with an explanatory note; the UI does not infer a 100% success rate from the presence of four successful result fixtures. Empty and malformed states are exposed through the same replaceable service boundary.

Model Status uses a typed `ModelService` boundary. `MockModelService` composes the existing prediction service to verify that all approved fixtures expose one deterministic demo version and threshold. It reads the master project specification for the planned dataset description, minimum engineered-feature requirement, serialization formats, and candidate-model inventory.

The service never converts planned requirements into completed artifact claims. Selected model, model family, training date, experiment tag, trained feature counts, calibration evidence, serialization status, MLflow experiment reference, and all candidate metrics remain unavailable. The current 50% threshold is identified only as a fixture-contract marker; it is not described as optimized or validated.

The Model page owns demo-state selection and presentation only. `MockModelService` owns source loading, consistency checks, current/planned separation, candidate normalization, unavailable-state construction, and safe error mapping. A future backend model-metadata adapter can replace it without redesigning the page.

Model Explanations uses a typed `ExplanationService` boundary. `MockExplanationService` composes the existing prediction and customer-detail services, then reads the approved fixture driver, explanation, impact, and recommendation fields. The UI does not calculate risk, infer drivers, or scatter customer-specific copy through page code.

The global preview aggregates only the four supplied fixture explanations. It groups approved drivers into contract, tenure, monthly-charge, payment-method, and device-protection families; ranks them by the sum of the absolute supplied demo contribution magnitudes; and labels direction as higher, lower, or mixed according to the fixture evidence. Relative influence is ordinal and normalized only for visual comparison. The page states that this is not SHAP, a population estimate, statistical feature importance, or causal evidence.

The local result preserves each fixture's current risk, label, three supplied drivers, plain-English explanations, contribution direction, supporting fixture values, and approved retention recommendation. Mixed higher- and lower-risk evidence is explicit for `CUST-HARD-001`. Unknown customer, no selection, empty, unavailable, malformed, and recoverable service-error states remain inside the same service/page boundary.

Customer Detail links the current fixture into Model Explanations using the canonical `fixture` query parameter. The Model page links to the explanation workspace without implying that trained explanation evidence exists.

The master specification names `/app/model/explanations`, but Streamlit 1.50 rejects nested page URL paths. The current router therefore exposes `/app/model-explanations`, following the existing flat-path adaptation used for Customer Detail. No proxy, rewrite, alternate framework, or duplicate customer experience was introduced.

A future backend adapter can implement `ExplanationService` and provide genuine model/SHAP evidence without redesigning the page. Evaluation metrics, calibration plots, statistically valid global importance, trained-model SHAP, monitoring, drift, latency, uptime, and deployment health remain intentionally outside the current frontend slice.
