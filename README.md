# ChurnGuard

ChurnGuard is a Streamlit customer churn analysis application combining a live ML prediction path with fixture-backed frontend workflows.

## Scope

- Score customer inputs using the registered MLflow XGBoost model.
- Display churn probability, a risk classification, and available local SHAP explanation drivers.
- Exercise input validation, prediction, and service-error handling.
- Explore fixture-backed customer history, customer details, batch workflows, analytics, model status, and explanation previews.
- Test local-artifact and registered-model prediction parity.
- Keep model evaluation evidence separate from claims about independent final performance.

Not every frontend workflow uses live model inference. Fixture-backed screens and explanations remain demo functionality unless explicitly connected to a live service.

## Routes

- `/app` — Command Center
- `/app/predict` — Customer Analysis and prediction
- `/app/customers` — Customer History
- `/app/customer-detail?fixture={customerId}` — Customer Detail
- `/app/batch` — Batch Prediction
- `/app/analytics` — Analytics
- `/app/model` — Model Status
- `/app/model-explanations?fixture={customerId}` — Model Explanations

Customer Detail uses a query parameter because Streamlit 1.50 page paths cannot contain nested dynamic segments. Model Explanations uses `/app/model-explanations` rather than the nested `/app/model/explanations` path.

## Requirements

- Python 3.11 or later
- Node.js and npm for frontend visual QA
- Python dependencies listed in `requirements.txt`

## Setup

### Python environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### Frontend QA dependencies

```powershell
npm install
npx playwright install chromium
```

## Run

From the project root:

```powershell
streamlit run frontend/streamlit_app/app.py
```

Open `http://localhost:8501/app`.

## Test

```powershell
python -m pip check
python -m pytest -q
python -m compileall -q frontend ml tests
npm run visual:qa
```

The visual QA script may require the Streamlit application to be running, depending on its implementation.

## Model and prediction

- Registered model: `ChurnGuard-XGBoost`, version `1`.
- MLflow model URI: `models:/ChurnGuard-XGBoost/1`.
- Current production decision threshold: `0.45`.
- Prediction integration: `frontend/streamlit_app/services/mlflow_prediction.py`.
- The prediction pipeline contains preprocessing and model steps.
- Local-versus-registered model parity is covered by `tests/test_model_parity.py`.
- The application can show local SHAP explanation drivers when available; the UI also supports a fallback when drivers are unavailable.

The production model and decision threshold should not be changed solely on the basis of exploratory evaluation results.

## Evaluation integrity

The historical holdout set was used to rank candidate models and select a decision threshold. Its reported metrics are therefore development-stage results, not an independent final performance estimate.

A separate nested cross-validation evaluation was conducted to assess model-selection and threshold-selection procedures within outer training folds. Its results are development-stage estimates, not a substitute for an untouched final holdout set.

The nested evaluation reported mean outer-fold results of approximately:

- Average precision: `0.668`
- ROC-AUC: `0.848`
- Precision: `0.500`
- Recall: `0.835`
- F1: `0.625`

These are cross-validation averages, not guaranteed production performance. Fold-level variability and the evaluation procedure should be reviewed alongside the averages.

The current production threshold remains `0.45`. Threshold sensitivity results are decision-support evidence, not authorization to change production configuration.

## Architecture

The application combines Streamlit UI components, service boundaries, fixture-backed demo workflows, and a live MLflow prediction integration.

- Live prediction uses the registered model through the prediction service.
- Some customer, batch, analytics, and explanation experiences remain fixture-backed.
- Demo explanation fixtures must not be represented as computed SHAP values.
- Fixture-backed analytics are not population-level production analytics.

## Sample data

`CHURNGUARD_SAMPLE_DATA.json` supplies deterministic demo fixtures for supported UI workflows. These fixtures are not real customer records, trained model outputs, population-level feature importance, or independent model evaluation data.

The Telco Customer Churn dataset used for model development is located at:

`ml/data/WA_Fn-UseC_-Telco-Customer-Churn.csv`

## Known limitations

- The dataset does not contain a genuine date/time field for a time-based holdout split.
- Historical holdout metrics are not independent final evaluation results because that holdout informed model and threshold selection.
- Nested cross-validation is a development-stage estimate; a genuinely untouched final evaluation cohort remains desirable.
- The available dataset and evaluation reports do not establish real-world business costs for false positives and false negatives.
- Some frontend pages and explanation previews remain fixture-backed.
- Batch processing and analytics are not equivalent to a persisted production customer platform.
- Production authentication, persistence, monitoring, deployment, and operational controls require separate validation.
- MLflow and SHAP currently emit dependency deprecation warnings in the tested environment.

## Reproducibility and artifacts

Python dependency versions are pinned in `requirements.txt`. `package-lock.json` should be committed after npm dependencies have been installed and verified.

Keep generated environments, `node_modules`, local MLflow databases, credentials, and other machine-specific files out of version control.
