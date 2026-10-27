from __future__ import annotations

from collections.abc import Mapping

from pydantic import ValidationError

from .models import CustomerInput


FIELD_LABELS: dict[str, str] = {
    "customerID": "Customer ID",
    "tenure": "Tenure",
    "MonthlyCharges": "Monthly charges",
    "TotalCharges": "Total charges",
}


def validate_customer(raw: Mapping[str, object]) -> tuple[CustomerInput | None, dict[str, str]]:
    try:
        return CustomerInput.model_validate(dict(raw)), {}
    except ValidationError as exc:
        errors: dict[str, str] = {}
        for issue in exc.errors():
            field = str(issue["loc"][0])
            label = FIELD_LABELS.get(field, field.replace("_", " ").title())
            kind = str(issue["type"])
            if kind == "missing" or kind == "string_too_short":
                message = f"{label} is required."
            elif kind in {"greater_than_equal", "less_than_equal", "int_parsing", "float_parsing"}:
                message = f"Enter a valid value for {label.lower()} within the allowed range."
            elif kind == "literal_error":
                message = f"Choose a supported value for {label.lower()}."
            else:
                message = f"Check the value for {label.lower()}."
            errors[field] = message
        return None, errors
