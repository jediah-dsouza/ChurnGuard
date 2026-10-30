# ChurnGuard

**An ML-powered customer churn analysis application built with Streamlit, XGBoost, and MLflow.**

ChurnGuard combines customer churn prediction, risk scoring, model explainability, customer analytics, and batch-analysis workflows in a unified interface. It integrates a registered MLflow model for live predictions with deterministic demo fixtures for selected frontend experiences.

> **Project status:** Portfolio and development-stage application. Some workflows are fixture-backed, and model evaluation results are development-stage estimates rather than guarantees of production performance.

## Features

- **Churn prediction:** Score customer inputs using the registered XGBoost model.
- **Risk assessment:** Display churn probabilities and risk classifications using a configurable decision threshold.
- **Model explainability:** Present available local SHAP explanation drivers, with a fallback when explanations are unavailable.
- **Customer exploration:** Browse customer history and individual customer details using deterministic demo fixtures.
- **Batch workflows:** Explore batch-prediction interfaces and associated workflows.
- **Customer analytics:** Review fixture-backed analytics and customer segments.
- **Model status:** Inspect model information and supporting evaluation evidence.
- **Evaluation integrity:** Document model-selection limitations, nested cross-validation results, and threshold sensitivity.
- **Automated QA:** Run Python tests, model-parity checks, and frontend visual and interaction tests.

## Technology stack

- **Language:** Python
- **Frontend:** Streamlit
- **Machine learning:** XGBoost, scikit-learn
- **Model lifecycle:** MLflow
- **Explainability:** SHAP
- **Testing:** pytest, Playwright
- **Frontend tooling:** Node.js and npm

## Application routes

| Route | Description |
|---|---|
| `/app` | Command Center |
| `/app/predict` | Customer Analysis and Prediction |
| `/app/customers` | Customer History |
| `/app/customer-detail?fixture={customerId}` | Customer Detail |
| `/app/batch` | Batch Prediction |
| `/app/analytics` | Analytics |
| `/app/model` | Model Status |
| `/app/model-explanations?fixture={customerId}` | Model Explanations |

Customer Detail and Model Explanations use query parameters to identify demo fixtures. Their implemented routes use flat page paths rather than nested dynamic URL segments.

## Requirements

- Python 3.11 or later
- Node.js and npm for frontend visual QA
- Python dependencies listed in `requirements.txt`
- Access to the registered MLflow model and its tracking/registry configuration for live prediction workflows
- The model-development dataset, obtained separately from a source whose usage and redistribution terms permit your intended use, for workflows that require it

## Quick start

Run the following commands from the project root.

### 1. Create and activate a Python environment

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

On macOS or Linux:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### 2. Configure model access

The live prediction integration uses the registered MLflow model:

`models:/ChurnGuard-XGBoost/1`

Configure MLflow tracking and registry access for your environment, and ensure the referenced model version is available before using live prediction workflows.

A fresh clone does not automatically include a developer's local MLflow tracking database or registry state. The model-development dataset is also excluded from version control.

Some frontend pages can be explored with deterministic fixtures without live model inference.

### 3. Launch the application

```powershell
streamlit run frontend/streamlit_app/app.py
```

Open:

[http://localhost:8501/app](http://localhost:8501/app)

The project configures Streamlit to use `/app` as its base URL path.

### 4. Install frontend QA dependencies

Node.js and npm are required for frontend visual QA.

```powershell
npm install
npx playwright install chromium
```

### 5. Run the tests

Check Python dependencies:

```powershell
python -m pip check
```

Run the Python test suite:

```powershell
python -m pytest -q
```

Compile the Python application and test modules:

```powershell
python -m compileall -q frontend ml tests
```

Run frontend visual QA:

```powershell
npm run visual:qa
```

Follow the visual QA script's requirements for whether the Streamlit application must already be running.

## Model and prediction

- **Registered model:** `ChurnGuard-XGBoost`, version `1`
- **MLflow model URI:** `models:/ChurnGuard-XGBoost/1`
- **Current production decision threshold:** `0.45`
- **Prediction integration:** `frontend/streamlit_app/services/mlflow_prediction.py`
- **Model parity tests:** `tests/test_model_parity.py`

The prediction pipeline includes preprocessing and model steps. The application can display local SHAP explanation drivers when available and provides a fallback when explanation drivers are unavailable.

The production model and decision threshold should not be changed solely on the basis of exploratory evaluation results.

## Evaluation integrity

The historical holdout set was used to rank candidate models and select a decision threshold. Consequently, the resulting holdout metrics are development-stage results, not an independent final performance estimate.

A separate nested cross-validation evaluation was conducted to assess model-selection and threshold-selection procedures within outer training folds. Its results provide development-stage estimates and are not a substitute for an untouched final holdout set.

The nested evaluation reported the following mean outer-fold results:

| Metric | Mean outer-fold result |
|---|---:|
| Average precision | `0.668` |
| ROC-AUC | `0.848` |
| Precision | `0.500` |
| Recall | `0.835` |
| F1 score | `0.625` |

These are cross-validation averages, not guaranteed production performance. Fold-level variability and the evaluation procedure should be reviewed alongside the averages.

The current production decision threshold remains `0.45`. Threshold-sensitivity results are decision-support evidence, not authorization to change production configuration.

A genuinely untouched final evaluation cohort remains desirable before making stronger claims about generalization.

## Architecture

ChurnGuard combines Streamlit UI components, service boundaries, fixture-backed demo workflows, and a live MLflow prediction integration.

- **Live inference:** Uses the registered model through the prediction service.
- **Demo workflows:** Some customer, batch, analytics, and explanation experiences use deterministic fixtures.
- **Explanation previews:** Fixture-backed explanations must not be represented as computed SHAP values.
- **Analytics:** Fixture-backed analytics are not population-level production analytics.
- **Model evaluation:** Reports document the limitations of historical holdout metrics and the role of nested cross-validation.

## Sample data and dataset availability

`CHURNGUARD_SAMPLE_DATA.json` contains deterministic demo fixtures for supported UI workflows.

These fixtures are not real customer records, trained model outputs, population-level feature importance, or independent model evaluation data.

The model-development dataset is expected at:

`ml/data/WA_Fn-UseC_-Telco-Customer-Churn.csv`

**The dataset is excluded from this repository.** Obtain it separately from an appropriately licensed source and verify the applicable usage and redistribution terms before using or sharing it. Workflows requiring this dataset will need it to be available locally.

## Known limitations

- The dataset does not contain a genuine date/time field suitable for a time-based holdout split.
- Historical holdout metrics are not independent final evaluation results because the holdout informed model and threshold selection.
- Nested cross-validation provides development-stage estimates; an untouched final evaluation cohort remains desirable.
- The available dataset and evaluation reports do not establish real-world business costs for false-positive and false-negative predictions.
- Some frontend pages and explanation previews remain fixture-backed.
- Batch processing and analytics are not equivalent to a persisted production customer platform.
- Production authentication, persistence, monitoring, deployment, and operational controls require separate validation.
- MLflow and SHAP emit dependency deprecation warnings in the tested environment.

## Reproducibility and artifacts

Python dependency versions are pinned in `requirements.txt`. The npm lockfile, `package-lock.json`, should remain committed to support consistent JavaScript dependency installation.

For reproducible live inference, the required MLflow tracking/registry configuration and registered model version must be available. Workflows that depend on the model-development dataset require that dataset to be obtained separately.

Keep virtual environments, `node_modules`, local MLflow databases, credentials, customer-level evaluation records, temporary files, and other machine-specific artifacts out of version control.

## Project structure

```text
ChurnGuard/
├── .streamlit/       # Streamlit configuration
├── design-system/    # Design-system documentation
├── docs/             # Architecture and QA evidence
├── frontend/         # Streamlit application and services
├── ml/               # Training, evaluation, models, and reports
├── scripts/          # Frontend QA tooling
├── tests/            # Python tests and model-parity checks
├── .gitignore
├── CHANGELOG.md
├── CHURNGUARD_SAMPLE_DATA.json
├── README.md
├── package.json
├── package-lock.json
├── pyproject.toml
└── requirements.txt
```

## Project goals

ChurnGuard demonstrates how a customer churn prediction workflow can be integrated into a structured application with model explainability, analytical interfaces, automated testing, and explicit documentation of evaluation limitations.

It is a development-stage decision-support application, not a claim of independently validated production performance.
