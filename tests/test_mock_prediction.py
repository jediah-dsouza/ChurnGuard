import pytest

from frontend.streamlit_app.models import PredictionRequest, RiskLabel
from frontend.streamlit_app.services import MockPredictionService, PredictionServiceError


@pytest.mark.parametrize(
    ("fixture_id", "probability", "label"),
    [
        ("CUST-LOW-001", 0.11, RiskLabel.LOW),
        ("CUST-HIGH-001", 0.87, RiskLabel.HIGH),
        ("CUST-BORDERLINE-001", 0.52, RiskLabel.MEDIUM),
        ("CUST-HARD-001", 0.61, RiskLabel.HIGH),
    ],
)
def test_required_fixture_predictions_are_deterministic(
    fixture_id: str, probability: float, label: RiskLabel
) -> None:
    service = MockPredictionService()
    customer = service.customer_for(fixture_id)
    result = service.predict(PredictionRequest(customer=customer))
    assert result.customer_id == fixture_id
    assert result.risk_probability == probability
    assert result.risk_label == label
    assert len(result.top_drivers) == 3
    assert result.is_demo_data is True
    assert result.model_version == "demo-fixture-v1.0.0"


def test_regression_pair_for_high_risk_fixture() -> None:
    service = MockPredictionService()
    customer = service.customer_for("CUST-HIGH-001")
    result = service.predict(PredictionRequest(customer=customer))
    assert result.prediction_id == "PRED-DEMO-HIGH-001"
    assert [driver.feature for driver in result.top_drivers] == [
        "Month-to-month contract",
        "Short tenure",
        "High monthly charges",
    ]
    assert result.recommendation.summary == "Prioritize this customer for retention outreach."


def test_edited_fixture_is_rejected_without_fake_inference() -> None:
    service = MockPredictionService()
    customer = service.customer_for("CUST-LOW-001").model_copy(update={"tenure": 47})
    with pytest.raises(PredictionServiceError, match="do not match"):
        service.predict(PredictionRequest(customer=customer))


def test_service_failure_then_retry_recovers() -> None:
    failing = MockPredictionService(fail_next=True)
    customer = failing.customer_for("CUST-HARD-001")
    request = PredictionRequest(customer=customer)
    with pytest.raises(PredictionServiceError, match="temporarily unavailable"):
        failing.predict(request)
    recovered = failing.predict(request)
    assert recovered.customer_id == "CUST-HARD-001"
    assert recovered.risk_probability == 0.61


def test_frontend_authentication_contract_is_explicitly_deferred() -> None:
    capabilities = MockPredictionService().capabilities
    assert capabilities.transport == "local-demo"
    assert capabilities.requires_authentication is False
