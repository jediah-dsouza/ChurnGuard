import pytest
from streamlit.testing.v1 import AppTest

from frontend.streamlit_app.models import DriverDirection, RiskLabel
from frontend.streamlit_app.services import (
    ExplanationDataError,
    ExplanationNotFound,
    ExplanationServiceError,
    MockExplanationService,
)


EXPLANATIONS_PATH = "frontend/streamlit_app/pages/model_explanations.py"
CUSTOMER_DETAIL_PATH = "frontend/streamlit_app/pages/customer_detail.py"
MODEL_PATH = "frontend/streamlit_app/pages/model.py"


def page_text(app: AppTest) -> str:
    return " ".join(item.value for item in app.markdown)


def click_button(app: AppTest, label: str) -> AppTest:
    button = next(item for item in app.button if item.label == label)
    return button.click().run()


def load_customer(app: AppTest, customer_id: str) -> AppTest:
    app.selectbox(key="explanation_customer").select(customer_id).run()
    return click_button(app, "Load demo explanation")


def test_explanation_service_contract_lists_approved_fixtures() -> None:
    assert MockExplanationService().fixture_ids() == [
        "CUST-LOW-001",
        "CUST-HIGH-001",
        "CUST-BORDERLINE-001",
        "CUST-HARD-001",
    ]


def test_global_explanation_is_deterministic_and_ranked() -> None:
    result = MockExplanationService().global_explanation()
    assert result.status == "populated"
    assert result.sample_size == 4
    assert result.is_demo_data is True
    assert [driver.family for driver in result.drivers] == [
        "Contract",
        "Tenure",
        "Monthly charges",
        "Payment method",
        "Device protection",
    ]
    assert [driver.rank for driver in result.drivers] == [1, 2, 3, 4, 5]
    assert result.drivers[0].direction == "mixed"
    assert result.drivers[0].relative_influence == "Highest in demo"
    assert result.drivers[0].observed_count == 4
    assert result.drivers[0].bar_percent == pytest.approx(100)
    assert "not SHAP" in result.methodology_note


def test_global_explanation_direction_patterns_match_fixtures() -> None:
    drivers = {
        driver.family: driver
        for driver in MockExplanationService().global_explanation().drivers
    }
    assert drivers["Tenure"].direction == "mixed"
    assert drivers["Monthly charges"].direction == "higher"
    assert drivers["Payment method"].direction == "mixed"
    assert drivers["Device protection"].direction == "lower"


@pytest.mark.parametrize(
    ("mode", "expected_status"),
    [("empty", "empty"), ("unavailable", "unavailable")],
)
def test_global_empty_and_unavailable_states(
    mode: str,
    expected_status: str,
) -> None:
    result = MockExplanationService().global_explanation(mode=mode)  # type: ignore[arg-type]
    assert result.status == expected_status
    assert result.drivers == []
    assert result.sample_size == 0


def test_global_malformed_and_service_error_contracts() -> None:
    service = MockExplanationService()
    with pytest.raises(ExplanationDataError, match="could not be interpreted"):
        service.global_explanation(mode="malformed")
    with pytest.raises(ExplanationServiceError, match="temporarily unavailable"):
        service.global_explanation(mode="error")


@pytest.mark.parametrize(
    ("fixture_id", "probability", "risk_label", "conflicting", "balancing"),
    [
        ("CUST-LOW-001", 0.11, RiskLabel.LOW, False, 3),
        ("CUST-HIGH-001", 0.87, RiskLabel.HIGH, False, 0),
        ("CUST-BORDERLINE-001", 0.52, RiskLabel.MEDIUM, True, 1),
        ("CUST-HARD-001", 0.61, RiskLabel.HIGH, True, 1),
    ],
)
def test_local_explanations_preserve_fixture_risk_and_signal_structure(
    fixture_id: str,
    probability: float,
    risk_label: RiskLabel,
    conflicting: bool,
    balancing: int,
) -> None:
    result = MockExplanationService().local_explanation(fixture_id)
    assert result.status == "populated"
    assert result.customer_id == fixture_id
    assert result.risk_probability == probability
    assert result.risk_label == risk_label
    assert result.threshold == 0.5
    assert len(result.drivers) == 3
    assert result.conflicting_signals is conflicting
    assert len(result.balancing_factors) == balancing
    assert result.is_demo_data is True


def test_local_driver_content_uses_existing_fixture_copy() -> None:
    result = MockExplanationService().local_explanation("CUST-HIGH-001")
    assert [driver.feature for driver in result.drivers] == [
        "Month-to-month contract",
        "Short tenure",
        "High monthly charges",
    ]
    assert [driver.demo_contribution for driver in result.drivers] == [
        0.44,
        0.36,
        0.25,
    ]
    assert all(
        driver.direction == DriverDirection.INCREASES
        for driver in result.drivers
    )
    assert result.operator_readout == (
        "Prioritize this customer for retention outreach."
    )


def test_hard_case_retains_competing_evidence() -> None:
    result = MockExplanationService().local_explanation("CUST-HARD-001")
    assert result.conflicting_signals is True
    assert [driver.direction for driver in result.drivers] == [
        DriverDirection.INCREASES,
        DriverDirection.INCREASES,
        DriverDirection.DECREASES,
    ]
    assert result.balancing_factors[0].feature == "One-year contract"
    assert "Conflicting signals" in result.plain_english_summary
    assert "review-worthy" in (result.operator_readout or "")


def test_local_unknown_unavailable_malformed_and_error_contracts() -> None:
    service = MockExplanationService()
    with pytest.raises(ExplanationNotFound):
        service.local_explanation("UNKNOWN")

    unavailable = service.local_explanation(
        "CUST-HIGH-001",
        mode="unavailable",
    )
    assert unavailable.status == "unavailable"
    assert unavailable.drivers == []
    assert unavailable.risk_probability == 0.87

    with pytest.raises(ExplanationDataError):
        service.local_explanation("CUST-HIGH-001", mode="malformed")
    with pytest.raises(ExplanationServiceError):
        service.local_explanation("CUST-HIGH-001", mode="error")


def test_explanations_page_initial_and_global_populated_state() -> None:
    app = AppTest.from_file(EXPLANATIONS_PATH, default_timeout=10).run()
    assert not app.exception
    text = page_text(app)
    assert "Demo explanation data" in text
    assert "Demo explanation view" in text
    assert "Contract" in text
    assert "Highest in demo" in text
    assert "No customer explanation selected" in text


def test_explanations_page_loads_high_risk_customer() -> None:
    app = AppTest.from_file(EXPLANATIONS_PATH, default_timeout=10).run()
    app = load_customer(app, "CUST-HIGH-001")
    text = page_text(app)
    assert not app.exception
    assert "87% · High" in text
    assert "Month-to-month contract" in text
    assert "Higher-risk signal" in text
    assert "Prioritize this customer for retention outreach." in text
    assert "not SHAP" in text


def test_explanations_page_shows_borderline_and_hard_mixed_signals() -> None:
    borderline = AppTest.from_file(
        EXPLANATIONS_PATH,
        default_timeout=10,
    ).run()
    borderline = load_customer(borderline, "CUST-BORDERLINE-001")
    assert "Mixed signals" in page_text(borderline)
    assert "52% · Medium / Review" in page_text(borderline)

    hard = AppTest.from_file(EXPLANATIONS_PATH, default_timeout=10).run()
    hard = load_customer(hard, "CUST-HARD-001")
    text = page_text(hard)
    assert "61% · High" in text
    assert "One-year contract" in text
    assert "Lower-risk signal" in text
    assert "review-worthy" in text


@pytest.mark.parametrize(
    ("state", "expected"),
    [
        ("Empty demo view", "No global explanation rows"),
        ("Explanation unavailable", "Global explanation unavailable"),
    ],
)
def test_global_page_empty_and_unavailable_states(
    state: str,
    expected: str,
) -> None:
    app = AppTest.from_file(EXPLANATIONS_PATH, default_timeout=10).run()
    app.selectbox(key="global_explanation_mode").select(state).run()
    assert expected in page_text(app)


@pytest.mark.parametrize(
    ("state", "expected"),
    [
        ("Malformed global data", "could not be interpreted"),
        ("Global service error", "could not be loaded"),
    ],
)
def test_global_page_error_states_and_recovery(
    state: str,
    expected: str,
) -> None:
    app = AppTest.from_file(EXPLANATIONS_PATH, default_timeout=10).run()
    app.selectbox(key="global_explanation_mode").select(state).run()
    assert expected in app.error[0].value
    app = click_button(app, "Retry global explanation")
    assert not app.error
    assert "Demo explanation view" in page_text(app)


def test_local_page_unavailable_state() -> None:
    app = AppTest.from_file(EXPLANATIONS_PATH, default_timeout=10).run()
    app.selectbox(key="local_explanation_mode").select(
        "Explanation unavailable"
    ).run()
    app = load_customer(app, "CUST-HIGH-001")
    text = page_text(app)
    assert "No explanation available for CUST-HIGH-001" in text
    assert "87% High demo risk remains available" in text


@pytest.mark.parametrize(
    ("state", "expected"),
    [
        ("Malformed explanation", "cannot be interpreted"),
        ("Local service error", "service unavailable"),
    ],
)
def test_local_page_error_and_recovery(state: str, expected: str) -> None:
    app = AppTest.from_file(EXPLANATIONS_PATH, default_timeout=10).run()
    app.selectbox(key="local_explanation_mode").select(state).run()
    app = load_customer(app, "CUST-HARD-001")
    assert expected in page_text(app)
    app = click_button(app, "Retry customer explanation")
    assert "61% · High" in page_text(app)
    assert "Mixed signals" in page_text(app)


def test_query_parameter_loads_customer_and_unknown_is_safe() -> None:
    known = AppTest.from_file(EXPLANATIONS_PATH, default_timeout=10)
    known.query_params["fixture"] = "CUST-LOW-001"
    known.run()
    assert not known.exception
    assert "11% · Low" in page_text(known)

    unknown = AppTest.from_file(EXPLANATIONS_PATH, default_timeout=10)
    unknown.query_params["fixture"] = "UNKNOWN"
    unknown.run()
    assert not unknown.exception
    assert "Customer explanation not found" in page_text(unknown)
    assert "UNKNOWN is not available" in page_text(unknown)


def test_customer_detail_and_model_link_to_explanations() -> None:
    detail = AppTest.from_file(CUSTOMER_DETAIL_PATH, default_timeout=10)
    detail.query_params["fixture"] = "CUST-HIGH-001"
    detail.run()
    assert (
        'href="/app/model-explanations?fixture=CUST-HIGH-001"'
        in page_text(detail)
    )

    model = AppTest.from_file(MODEL_PATH, default_timeout=10).run()
    assert 'href="/app/model-explanations"' in page_text(model)


def test_explanations_page_includes_loading_and_navigation_contracts() -> None:
    source = open(EXPLANATIONS_PATH, encoding="utf-8").read()
    assert 'st.spinner("Loading deterministic explanation…")' in source
    app = AppTest.from_file(EXPLANATIONS_PATH, default_timeout=10).run()
    app = load_customer(app, "CUST-LOW-001")
    text = page_text(app)
    assert 'href="/app/customer-detail?fixture=CUST-LOW-001"' in text
    assert 'href="/app/predict?fixture=CUST-LOW-001"' in text