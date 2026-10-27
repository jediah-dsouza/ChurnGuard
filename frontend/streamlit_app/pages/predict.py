
from __future__ import annotations

import sys
from pathlib import Path
from typing import cast

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from frontend.streamlit_app.models import (
    CustomerInput,
    PredictionRequest,
    PredictionResponse,
)
from frontend.streamlit_app.services import (
    MockPredictionService,
    PredictionServiceError,
)
from frontend.streamlit_app.services.mlflow_prediction import (
    MLflowPredictionService,
)
from frontend.streamlit_app.ui.components import (
    app_shell,
    empty_result,
    page_header,
    render_prediction,
)
from frontend.streamlit_app.validation import validate_customer


@st.cache_resource
def get_service() -> MockPredictionService:
    """Loads the approved sample-customer fixtures."""
    return MockPredictionService()


@st.cache_resource
def get_model_service() -> MLflowPredictionService:
    """Loads the registered XGBoost model once per Streamlit process."""
    return MLflowPredictionService()


def initialize_state(service: MockPredictionService) -> None:
    if "selected_fixture" not in st.session_state:
        st.session_state.selected_fixture = "CUST-HARD-001"

    if "result" not in st.session_state:
        st.session_state.result = None

    if "service_error" not in st.session_state:
        st.session_state.service_error = None

    if "last_valid_customer" not in st.session_state:
        st.session_state.last_valid_customer = None

    if "validation_errors" not in st.session_state:
        st.session_state.validation_errors = {}

    if "form_customer" not in st.session_state:
        st.session_state.form_customer = (
            service.customer_for("CUST-HARD-001").model_dump(
                by_alias=True
            )
        )


def load_fixture(
    service: MockPredictionService,
    fixture_id: str,
) -> None:
    """Loads a sample customer into the editable form."""
    fixture = service.customer_for(fixture_id).model_dump(
        by_alias=True
    )

    st.session_state.form_customer = fixture
    st.session_state.result = None
    st.session_state.service_error = None
    st.session_state.validation_errors = {}

    for field, value in fixture.items():
        if field in {"tenure", "MonthlyCharges", "TotalCharges"}:
            st.session_state[f"field_{field}"] = str(value)
        else:
            st.session_state[f"field_{field}"] = value



def run_prediction(
    customer: CustomerInput,
    *,
    force_failure: bool = False,
) -> None:
    """Scores the submitted customer with the registered MLflow model."""
    try:
        if force_failure:
            raise PredictionServiceError(
                "Simulated service failure. Your input has been preserved."
            )

        model_service = get_model_service()

        customer_data = customer.model_dump(by_alias=True)
        customer_id = customer_data.get("customerID", "unknown")

        with st.spinner(
            "Scoring customer with the registered XGBoost model..."
        ):
            result = model_service.predict(
                PredictionRequest(customer=customer)
            )

        # Diagnostic logging: verify the actual prediction result.
        result_data = result.model_dump(by_alias=True)

        probability = result_data.get("riskProbability")
        model_version = result_data.get("modelVersion")
        is_demo_data = result_data.get("isDemoData")

        print(
            "[MLflow prediction] "
            f"customer_id={customer_id}, "
            f"probability={probability}, "
            f"model={model_version}, "
            f"is_demo_data={is_demo_data}",
            flush=True,
        )

        st.session_state.result = result
        st.session_state.last_valid_customer = customer
        st.session_state.service_error = None

    except PredictionServiceError as exc:
        st.session_state.result = None
        st.session_state.last_valid_customer = customer
        st.session_state.service_error = str(exc)

    except Exception as exc:
        st.session_state.result = None
        st.session_state.last_valid_customer = customer
        st.session_state.service_error = (
            "The model prediction failed unexpectedly. "
            "Your input has been preserved. "
            f"Error: {type(exc).__name__}: {exc}"
        )


service = get_service()
initialize_state(service)

# Support links to this page that specify a sample fixture.
requested_fixture = st.query_params.get("fixture")

fixture_ids = {
    str(item["fixtureId"])
    for item in service.fixtures()
    if isinstance(item.get("fixtureId"), str)
}

if (
    isinstance(requested_fixture, str)
    and requested_fixture in fixture_ids
    and st.session_state.get("route_fixture") != requested_fixture
):
    load_fixture(service, requested_fixture)
    st.session_state.selected_fixture = requested_fixture
    st.session_state.route_fixture = requested_fixture

app_shell("Analyze customer")
page_header()

fixtures = service.fixtures()

fixture_labels = {
    cast(str, item["fixtureId"]): (
        f'{item["fixtureId"]} — '
        f'{str(item["scenario"]).replace("_", " ").title()}'
    )
    for item in fixtures
}

selector_col, note_col = st.columns([1.15, 1], gap="large")

with selector_col:
    selected_fixture = st.selectbox(
        "Sample customer",
        options=list(fixture_labels),
        format_func=lambda fixture_id: fixture_labels[fixture_id],
        key="selected_fixture",
        help="Loads starting values from CHURNGUARD_SAMPLE_DATA.json.",
    )

with note_col:
    st.markdown("**Model behavior**")
    st.caption(
        "Sample customers are starting points. "
        "Edited values are scored by the registered XGBoost model."
    )

st.button(
    "Load selected customer",
    use_container_width=False,
    on_click=load_fixture,
    args=(service, selected_fixture),
)

raw = cast(dict[str, object], st.session_state.form_customer)

left, right = st.columns([0.92, 1.08], gap="large")

with left:
    st.subheader("Customer input")
    st.caption(
        "Required fields · values are preserved after validation "
        "or prediction errors."
    )

    with st.form("customer-form", border=True):
        st.markdown("#### Profile")

        raw["customerID"] = st.text_input(
            "Customer ID",
            value=str(raw["customerID"]),
            key="field_customerID",
        )

        if "customerID" in st.session_state.validation_errors:
            st.markdown(
                (
                    '<div class="cg-field-error">⚠ '
                    f'{st.session_state.validation_errors["customerID"]}'
                    "</div>"
                ),
                unsafe_allow_html=True,
            )

        profile_a, profile_b = st.columns(2)

        with profile_a:
            raw["gender"] = st.selectbox(
                "Gender",
                ["Female", "Male"],
                index=["Female", "Male"].index(str(raw["gender"])),
                key="field_gender",
            )

            raw["SeniorCitizen"] = (
                1
                if st.checkbox(
                    "Senior citizen",
                    value=bool(raw["SeniorCitizen"]),
                    key="field_SeniorCitizen",
                )
                else 0
            )

        with profile_b:
            raw["Partner"] = st.selectbox(
                "Partner",
                ["Yes", "No"],
                index=["Yes", "No"].index(str(raw["Partner"])),
                key="field_Partner",
            )

            raw["Dependents"] = st.selectbox(
                "Dependents",
                ["Yes", "No"],
                index=["Yes", "No"].index(str(raw["Dependents"])),
                key="field_Dependents",
            )

        st.markdown("#### Account")
        account_a, account_b = st.columns(2)

        with account_a:
            raw["tenure"] = st.text_input(
                "Tenure (months)",
                value=str(raw["tenure"]),
                key="field_tenure",
            )

            if "tenure" in st.session_state.validation_errors:
                st.markdown(
                    (
                        '<div class="cg-field-error">⚠ '
                        f'{st.session_state.validation_errors["tenure"]}'
                        "</div>"
                    ),
                    unsafe_allow_html=True,
                )

            raw["Contract"] = st.selectbox(
                "Contract",
                ["Month-to-month", "One year", "Two year"],
                index=[
                    "Month-to-month",
                    "One year",
                    "Two year",
                ].index(str(raw["Contract"])),
                key="field_Contract",
            )

            raw["PaymentMethod"] = st.selectbox(
                "Payment method",
                [
                    "Electronic check",
                    "Mailed check",
                    "Bank transfer (automatic)",
                    "Credit card (automatic)",
                ],
                index=[
                    "Electronic check",
                    "Mailed check",
                    "Bank transfer (automatic)",
                    "Credit card (automatic)",
                ].index(str(raw["PaymentMethod"])),
                key="field_PaymentMethod",
            )

        with account_b:
            raw["MonthlyCharges"] = st.text_input(
                "Monthly charges ($)",
                value=str(raw["MonthlyCharges"]),
                key="field_MonthlyCharges",
            )

            if "MonthlyCharges" in st.session_state.validation_errors:
                st.markdown(
                    (
                        '<div class="cg-field-error">⚠ '
                        f'{st.session_state.validation_errors["MonthlyCharges"]}'
                        "</div>"
                    ),
                    unsafe_allow_html=True,
                )

            raw["TotalCharges"] = st.text_input(
                "Total charges ($)",
                value=str(raw["TotalCharges"]),
                key="field_TotalCharges",
            )

            if "TotalCharges" in st.session_state.validation_errors:
                st.markdown(
                    (
                        '<div class="cg-field-error">⚠ '
                        f'{st.session_state.validation_errors["TotalCharges"]}'
                        "</div>"
                    ),
                    unsafe_allow_html=True,
                )

            raw["PaperlessBilling"] = st.selectbox(
                "Paperless billing",
                ["Yes", "No"],
                index=["Yes", "No"].index(
                    str(raw["PaperlessBilling"])
                ),
                key="field_PaperlessBilling",
            )

        with st.expander("Services", expanded=False):
            service_a, service_b = st.columns(2)

            fields = [
                ("PhoneService", "Phone service", ["Yes", "No"]),
                ("MultipleLines", "Multiple lines", ["Yes", "No"]),
                (
                    "InternetService",
                    "Internet service",
                    ["DSL", "Fiber optic", "No"],
                ),
                ("OnlineSecurity", "Online security", ["Yes", "No"]),
                ("OnlineBackup", "Online backup", ["Yes", "No"]),
                (
                    "DeviceProtection",
                    "Device protection",
                    ["Yes", "No"],
                ),
                ("TechSupport", "Tech support", ["Yes", "No"]),
                ("StreamingTV", "Streaming TV", ["Yes", "No"]),
                (
                    "StreamingMovies",
                    "Streaming movies",
                    ["Yes", "No"],
                ),
            ]

            for index, (key, label, options) in enumerate(fields):
                target = service_a if index % 2 == 0 else service_b

                with target:
                    raw[key] = st.selectbox(
                        label,
                        options,
                        index=options.index(str(raw[key])),
                        key=f"field_{key}",
                    )

        force_failure = st.checkbox(
            "Simulate one service failure",
            help=(
                "Development-only control for testing error handling. "
                "When selected, the model will not be called."
            ),
        )

        submitted = st.form_submit_button(
            "Run model prediction",
            use_container_width=True,
        )

    if st.session_state.validation_errors:
        st.error(
            "Prediction not run. Correct the highlighted field messages."
        )

    if submitted:
        customer, errors = validate_customer(raw)

        if errors:
            st.session_state.result = None
            st.session_state.service_error = None
            st.session_state.validation_errors = errors
            st.rerun()

        elif customer is not None:
            st.session_state.validation_errors = {}
            st.session_state.form_customer = customer.model_dump(
                by_alias=True
            )

            run_prediction(
                customer,
                force_failure=force_failure,
            )
            st.rerun()


with right:
    st.subheader("Risk brief")
    st.caption(
        "Decision support from the registered XGBoost model. "
        "Predictions are estimates, not confirmed customer outcomes."
    )

    if st.session_state.service_error:
        st.error(
            st.session_state.service_error,
            icon="⚠️",
        )

        st.caption(
            "Your last validated customer input has been preserved. "
            "Retry the model prediction when ready."
        )

        if st.button("Retry model prediction"):
            customer = st.session_state.last_valid_customer

            if customer is not None:
                run_prediction(customer)
                st.rerun()
            else:
                st.warning("Submit valid customer details before retrying.")

    elif st.session_state.result:
        result = cast(
            PredictionResponse,
            st.session_state.result,
        )
        customer = cast(
            CustomerInput,
            st.session_state.last_valid_customer,
        )

        if result.is_demo_data:
            st.warning(
                "This result is marked as demo data. "
                "It should not be treated as a live model prediction."
            )
        else:
            st.success(
                f"Model: {result.model_version} · "
                f"Decision threshold: {result.threshold:.0%}"
            )

        render_prediction(result, customer)

        if st.button("Edit and re-run", use_container_width=False):
            st.session_state.result = None
            st.rerun()

    else:
        empty_result()
