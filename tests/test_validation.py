from copy import deepcopy

from frontend.streamlit_app.services import MockPredictionService
from frontend.streamlit_app.validation import validate_customer


def fixture_customer() -> dict[str, object]:
    service = MockPredictionService()
    return service.customer_for("CUST-LOW-001").model_dump(by_alias=True)


def test_valid_customer_passes() -> None:
    customer, errors = validate_customer(fixture_customer())
    assert customer is not None
    assert errors == {}


def test_missing_required_fields_are_rejected() -> None:
    raw = fixture_customer()
    raw["customerID"] = ""
    raw.pop("tenure")
    customer, errors = validate_customer(raw)
    assert customer is None
    assert "customerID" in errors
    assert "tenure" in errors


def test_invalid_numeric_range_is_rejected() -> None:
    raw = fixture_customer()
    raw["tenure"] = -1
    customer, errors = validate_customer(raw)
    assert customer is None
    assert "tenure" in errors


def test_unseen_category_is_rejected() -> None:
    raw = deepcopy(fixture_customer())
    raw["Contract"] = "Weekly"
    customer, errors = validate_customer(raw)
    assert customer is None
    assert errors["Contract"] == "Choose a supported value for contract."
