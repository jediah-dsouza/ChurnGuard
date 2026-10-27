from __future__ import annotations

from collections import defaultdict
from typing import Literal

from ..models import (
    DriverDirection,
    ExplanationDriverItem,
    GlobalExplanationDriver,
    GlobalExplanationResult,
    LocalExplanationResult,
)
from .contract import (
    ExplanationDataError,
    ExplanationNotFound,
    ExplanationServiceError,
)
from .customer_detail import (
    CustomerDetailDataError,
    CustomerDetailNotFound,
    MockCustomerDetailService,
)
from .mock_prediction import MockPredictionService


GlobalExplanationMode = Literal[
    "sample",
    "empty",
    "unavailable",
    "malformed",
    "error",
]
LocalExplanationMode = Literal["sample", "unavailable", "malformed", "error"]


class MockExplanationService:
    """Builds deterministic explanation previews from approved prediction fixtures."""

    FAMILY_MEANINGS = {
        "Contract": (
            "Contract commitment changes how easily a customer can leave; "
            "the direction varies by the supplied contract term."
        ),
        "Tenure": (
            "The supplied fixtures distinguish short or developing tenure "
            "from a long-standing customer relationship."
        ),
        "Monthly charges": (
            "Higher recurring charges contribute to concern in the supplied "
            "high-risk and hard-case fixtures."
        ),
        "Payment method": (
            "Payment method appears as either a higher- or lower-risk signal "
            "depending on the approved fixture."
        ),
        "Device protection": (
            "An additional service relationship lowers the demo signal in "
            "the approved borderline fixture."
        ),
    }

    def __init__(
        self,
        prediction_service: MockPredictionService | None = None,
        detail_service: MockCustomerDetailService | None = None,
    ) -> None:
        self._predictions = prediction_service or MockPredictionService()
        self._details = detail_service or MockCustomerDetailService(
            self._predictions
        )

    def fixture_ids(self) -> list[str]:
        identifiers = []
        for fixture in self._predictions.fixtures():
            fixture_id = fixture.get("fixtureId")
            if not isinstance(fixture_id, str):
                raise ExplanationDataError(
                    "The demo explanation fixture list has an invalid format."
                )
            identifiers.append(fixture_id)
        return identifiers

    def global_explanation(
        self,
        *,
        mode: GlobalExplanationMode = "sample",
    ) -> GlobalExplanationResult:
        if mode == "malformed":
            raise ExplanationDataError(
                "The demo global explanation data could not be interpreted."
            )
        if mode == "error":
            raise ExplanationServiceError(
                "The demo explanation service is temporarily unavailable."
            )
        note = (
            "Demo explanation view based on the four approved sample fixtures. "
            "Relative influence aggregates supplied UI-fixture contributions; "
            "it is not SHAP or a production feature-importance estimate."
        )
        if mode in {"empty", "unavailable"}:
            return GlobalExplanationResult(
                status=mode,
                drivers=[],
                sample_size=0,
                methodology_note=note,
                is_demo_data=True,
            )

        contributions: dict[str, list[tuple[DriverDirection, float]]] = defaultdict(
            list
        )
        fixture_ids = self.fixture_ids()
        for fixture_id in fixture_ids:
            local = self.local_explanation(fixture_id)
            for driver in local.drivers:
                contributions[driver.family].append(
                    (driver.direction, abs(driver.demo_contribution))
                )
        if not contributions:
            raise ExplanationDataError(
                "The demo global explanation data contains no drivers."
            )

        totals = {
            family: sum(value for _, value in values)
            for family, values in contributions.items()
        }
        maximum = max(totals.values())
        ordered = sorted(
            totals,
            key=lambda family: (-totals[family], family),
        )
        labels = ["Highest in demo", "Strong", "Moderate", "Limited", "Narrow"]
        drivers = []
        for index, family in enumerate(ordered, start=1):
            directions = {
                direction for direction, _ in contributions[family]
            }
            direction = (
                "mixed"
                if len(directions) > 1
                else "higher"
                if DriverDirection.INCREASES in directions
                else "lower"
            )
            drivers.append(
                GlobalExplanationDriver(
                    rank=index,
                    family=family,
                    direction=direction,
                    relative_influence=labels[min(index - 1, len(labels) - 1)],
                    observed_count=len(contributions[family]),
                    meaning=self.FAMILY_MEANINGS.get(
                        family,
                        "This signal appears in the approved explanation fixtures.",
                    ),
                    bar_percent=totals[family] / maximum * 100,
                )
            )
        return GlobalExplanationResult(
            status="populated",
            drivers=drivers,
            sample_size=len(fixture_ids),
            methodology_note=note,
            is_demo_data=True,
        )

    def local_explanation(
        self,
        customer_id: str,
        *,
        mode: LocalExplanationMode = "sample",
    ) -> LocalExplanationResult:
        if mode == "malformed":
            raise ExplanationDataError(
                "The demo customer explanation data could not be interpreted."
            )
        if mode == "error":
            raise ExplanationServiceError(
                "The demo explanation service is temporarily unavailable."
            )
        try:
            detail = self._details.detail(customer_id)
        except CustomerDetailNotFound as exc:
            raise ExplanationNotFound(customer_id) from exc
        except CustomerDetailDataError as exc:
            raise ExplanationDataError(
                "The demo customer explanation data could not be interpreted."
            ) from exc

        prediction = detail.prediction
        if mode == "unavailable":
            return LocalExplanationResult(
                status="unavailable",
                customer_id=customer_id,
                risk_probability=prediction.risk_probability,
                risk_label=prediction.risk_label,
                threshold=prediction.threshold,
                drivers=[],
                balancing_factors=[],
                conflicting_signals=False,
                plain_english_summary=(
                    "No deterministic explanation is available for this customer."
                ),
                operator_readout=None,
                actions=[],
                model_version=prediction.model_version,
                explanation_status="Demo explanation unavailable",
                is_demo_data=True,
            )

        drivers = [
            ExplanationDriverItem(
                rank=index,
                feature=driver.feature,
                family=self._family(driver.feature),
                direction=driver.direction,
                demo_contribution=driver.impact,
                explanation=driver.explanation,
                supporting_value=supporting_value,
            )
            for index, (driver, supporting_value) in enumerate(
                zip(
                    prediction.top_drivers,
                    detail.driver_values,
                    strict=True,
                ),
                start=1,
            )
        ]
        directions = {driver.direction for driver in drivers}
        return LocalExplanationResult(
            status="populated",
            customer_id=customer_id,
            risk_probability=prediction.risk_probability,
            risk_label=prediction.risk_label,
            threshold=prediction.threshold,
            drivers=drivers,
            balancing_factors=[
                driver
                for driver in drivers
                if driver.direction == DriverDirection.DECREASES
            ],
            conflicting_signals=len(directions) > 1,
            plain_english_summary=prediction.scenario_description,
            operator_readout=prediction.recommendation.summary,
            actions=list(prediction.recommendation.actions),
            model_version=prediction.model_version,
            explanation_status="Deterministic demo explanation",
            is_demo_data=True,
        )

    @staticmethod
    def _family(feature: str) -> str:
        normalized = feature.casefold()
        if "contract" in normalized:
            return "Contract"
        if "tenure" in normalized:
            return "Tenure"
        if "monthly charges" in normalized:
            return "Monthly charges"
        if (
            "payment" in normalized
            or "electronic check" in normalized
            or "bank transfer" in normalized
        ):
            return "Payment method"
        if "device protection" in normalized:
            return "Device protection"
        return feature