from __future__ import annotations

from typing import Literal

from ..models import (
    CustomerDetailResult,
    CustomerInput,
    PredictionRequest,
)
from .contract import PredictionServiceError
from .mock_prediction import MockPredictionService


CustomerDetailMode = Literal["sample", "malformed"]


class CustomerDetailNotFound(LookupError):
    """The requested deterministic customer does not exist."""


class CustomerDetailDataError(RuntimeError):
    """Safe customer-detail failure for the recoverable UI state."""


class MockCustomerDetailService:
    """Loads one approved fixture through the existing prediction service."""

    def __init__(self, prediction_service: MockPredictionService | None = None) -> None:
        self._predictions = prediction_service or MockPredictionService()

    def detail(
        self,
        customer_id: str,
        *,
        mode: CustomerDetailMode = "sample",
    ) -> CustomerDetailResult:
        if mode == "malformed":
            raise CustomerDetailDataError(
                "The demo customer record could not be prepared."
            )
        try:
            customer = self._predictions.customer_for(customer_id)
        except PredictionServiceError as exc:
            raise CustomerDetailNotFound(customer_id) from exc

        try:
            prediction = self._predictions.predict(
                PredictionRequest(customer=customer)
            )
        except PredictionServiceError as exc:
            raise CustomerDetailDataError(
                "The demo customer record could not be prepared."
            ) from exc

        return CustomerDetailResult(
            customer=customer,
            prediction=prediction,
            driver_values=[
                self._supporting_value(customer, driver.feature)
                for driver in prediction.top_drivers
            ],
            service_status="Demo fixture service available",
        )

    @staticmethod
    def _supporting_value(customer: CustomerInput, feature: str) -> str | None:
        """Return only a fixture value directly represented by a driver label."""
        normalized = feature.casefold()
        if "contract" in normalized:
            return customer.contract
        if "tenure" in normalized:
            return f"{customer.tenure} months"
        if "monthly charges" in normalized:
            return f"${customer.monthly_charges:,.2f} / month"
        if "payment" in normalized or "electronic check" in normalized:
            return customer.payment_method
        if "bank transfer" in normalized:
            return customer.payment_method
        if "device protection" in normalized:
            return customer.device_protection
        return None