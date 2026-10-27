import pytest
from streamlit.testing.v1 import AppTest

from frontend.streamlit_app.models import RiskLabel
from frontend.streamlit_app.services import (
    CustomerDetailDataError,
    CustomerDetailNotFound,
    MockCustomerDetailService,
)


CUSTOMER_DETAIL_PATH = "frontend/streamlit_app/pages/customer_detail.py"


@pytest.mark.parametrize(
    ("fixture_id", "probability", "risk_label"),
    [
        ("CUST-LOW-001", 0.11, RiskLabel.LOW),
        ("CUST-HIGH-001", 0.87, RiskLabel.HIGH),
        ("CUST-BORDERLINE-001", 0.52, RiskLabel.MEDIUM),
        ("CUST-HARD-001", 0.61, RiskLabel.HIGH),
    ],
)
def test_customer_detail_service_preserves_fixture_predictions(
    fixture_id: str,
    probability: float,
    risk_label: RiskLabel,
) -> None:
    detail = MockCustomerDetailService().detail(fixture_id)
    assert detail.customer.customer_id == fixture_id
    assert detail.prediction.risk_probability == probability
    assert detail.prediction.risk_label == risk_label
    assert len(detail.prediction.top_drivers) == 3
    assert len(detail.driver_values) == 3


def test_customer_detail_service_uses_fixture_values_for_driver_context() -> None:
    detail = MockCustomerDetailService().detail("CUST-HIGH-001")
    assert detail.driver_values == [
        "Month-to-month",
        "4 months",
        "$89.10 / month",
    ]


def test_customer_detail_service_unknown_and_error_contracts() -> None:
    with pytest.raises(CustomerDetailNotFound):
        MockCustomerDetailService().detail("UNKNOWN")
    with pytest.raises(CustomerDetailDataError, match="could not be prepared"):
        MockCustomerDetailService().detail("CUST-HIGH-001", mode="malformed")


def detail_app(fixture_id: str | None) -> AppTest:
    app = AppTest.from_file(CUSTOMER_DETAIL_PATH, default_timeout=10)
    if fixture_id is not None:
        app.query_params["fixture"] = fixture_id
    return app.run()


@pytest.mark.parametrize(
    ("fixture_id", "probability", "risk_copy"),
    [
        ("CUST-LOW-001", "11%", "LOW RISK"),
        ("CUST-HIGH-001", "87%", "HIGH RISK"),
        ("CUST-BORDERLINE-001", "52%", "MEDIUM / REVIEW"),
        ("CUST-HARD-001", "61%", "review-worthy hard case"),
    ],
)
def test_each_customer_detail_page_renders(
    fixture_id: str,
    probability: str,
    risk_copy: str,
) -> None:
    app = detail_app(fixture_id)
    assert not app.exception
    page_text = " ".join(item.value for item in app.markdown)
    assert fixture_id in page_text
    assert probability in page_text
    assert risk_copy in page_text


def test_customer_detail_renders_drivers_explanation_recommendation_and_context() -> None:
    app = detail_app("CUST-HIGH-001")
    page_text = " ".join(item.value for item in app.markdown)
    assert "Month-to-month contract" in page_text
    assert "The customer is not committed to a longer-term contract." in page_text
    assert "Short-tenure customer on a month-to-month contract" in page_text
    assert "Prioritize this customer for retention outreach." in page_text
    assert "Electronic check" in page_text
    assert "Fiber optic" in page_text
    assert "demo-fixture-v1.0.0" in page_text


def test_customer_detail_missing_fixture_state() -> None:
    app = detail_app(None)
    assert not app.exception
    assert "Select a customer" in [title.value for title in app.title]
    assert "No customer selected" in " ".join(item.value for item in app.markdown)


def test_customer_detail_unknown_fixture_state() -> None:
    app = detail_app("UNKNOWN")
    assert not app.exception
    assert "Customer not found" in [title.value for title in app.title]
    assert "UNKNOWN is not available" in " ".join(
        item.value for item in app.markdown
    )


def test_customer_detail_malformed_fixture_state_is_safe() -> None:
    app = detail_app("<script>alert(1)</script>")
    assert not app.exception
    page_text = " ".join(item.value for item in app.markdown)
    assert "Customer not found" in [title.value for title in app.title]
    assert "malformed and was not processed" in page_text
    assert "<script>" not in page_text


def test_customer_detail_recoverable_data_error_state() -> None:
    app = detail_app("CUST-HIGH-001")
    app.selectbox(key="customer_detail_mode").select("Malformed demo record").run()
    assert not app.exception
    assert "could not be loaded" in app.error[0].value
    assert any(button.label == "Retry customer fixture" for button in app.button)


def test_customer_detail_navigation_contracts() -> None:
    app = detail_app("CUST-HIGH-001")
    page_text = " ".join(item.value for item in app.markdown)
    assert 'href="/app/customers"' in page_text
    assert 'href="/app/predict?fixture=CUST-HIGH-001"' in page_text
    assert 'href="/app"' in page_text