from __future__ import annotations

from typing import Literal

from ..models import (
    CommandCenterKpis,
    CommandCenterSnapshot,
    PredictionHistoryRow,
    PredictionRequest,
    ReviewItem,
    RiskDistribution,
    RiskLabel,
)
from .mock_prediction import MockPredictionService


CommandCenterMode = Literal["sample", "empty", "malformed"]


class CommandCenterDataError(RuntimeError):
    """Safe command-center data failure for the frontend error state."""


class MockCommandCenterService:
    """Builds an operational demo snapshot from approved prediction fixtures."""

    def __init__(self, prediction_service: MockPredictionService | None = None) -> None:
        self._predictions = prediction_service or MockPredictionService()

    def snapshot(self, mode: CommandCenterMode = "sample") -> CommandCenterSnapshot:
        if mode == "malformed":
            raise CommandCenterDataError(
                "The demo activity snapshot could not be prepared."
            )
        if mode == "empty":
            return self._empty_snapshot()

        rows: list[PredictionHistoryRow] = []
        for fixture in self._predictions.fixtures():
            fixture_id = fixture.get("fixtureId")
            if not isinstance(fixture_id, str):
                raise CommandCenterDataError(
                    "The demo activity snapshot contains an invalid customer record."
                )
            try:
                customer = self._predictions.customer_for(fixture_id)
                prediction = self._predictions.predict(
                    PredictionRequest(customer=customer)
                )
            except Exception as exc:
                raise CommandCenterDataError(
                    "The demo activity snapshot could not be prepared."
                ) from exc
            rows.append(
                PredictionHistoryRow(
                    customer_id=prediction.customer_id,
                    risk_probability=prediction.risk_probability,
                    risk_label=prediction.risk_label,
                    top_driver=prediction.top_drivers[0].feature,
                    tenure=customer.tenure,
                    contract=customer.contract,
                    predicted_at=prediction.generated_at,
                    model_version=prediction.model_version,
                    threshold=prediction.threshold,
                    scenario=prediction.scenario,
                )
            )

        priority = {RiskLabel.HIGH: 0, RiskLabel.MEDIUM: 1, RiskLabel.LOW: 2}
        rows.sort(
            key=lambda row: (
                priority[row.risk_label],
                -row.risk_probability,
                row.customer_id,
            )
        )
        total = len(rows)
        high_count = sum(row.risk_label == RiskLabel.HIGH for row in rows)
        average = sum(row.risk_probability for row in rows) / total

        return CommandCenterSnapshot(
            rows=rows,
            kpis=CommandCenterKpis(
                predictions_analyzed=total,
                high_risk_customers=high_count,
                average_predicted_risk=average,
                recent_high_risk_share=high_count / total,
            ),
            distribution=RiskDistribution(
                low=sum(row.risk_label == RiskLabel.LOW for row in rows),
                medium=sum(row.risk_label == RiskLabel.MEDIUM for row in rows),
                high=high_count,
                threshold=rows[0].threshold,
            ),
            review_items=[
                ReviewItem(
                    reference="CUST-BORDERLINE-001",
                    category="prediction",
                    title="Near-threshold prediction",
                    detail="52% demo risk sits close to the 50% operating threshold.",
                    action="Inspect the mixed risk and retention signals.",
                ),
                ReviewItem(
                    reference="CUST-HARD-001",
                    category="prediction",
                    title="Conflicting customer signals",
                    detail="High charges raise risk while a one-year contract lowers it.",
                    action="Use operator review rather than an automatic conclusion.",
                ),
                ReviewItem(
                    reference="INVALID-MISSING-001",
                    category="input",
                    title="Incomplete-input test state",
                    detail="The supplied UI scenario omits customer ID and tenure.",
                    action="Validation blocks prediction until required values are restored.",
                ),
                ReviewItem(
                    reference="SERVICE-ERROR-001",
                    category="service",
                    title="Recoverable service test state",
                    detail="The supplied UI scenario forces one mock service failure.",
                    action="Retry reuses the preserved validated customer.",
                ),
            ],
            model_version=rows[0].model_version,
            generated_at=max(row.predicted_at for row in rows),
            service_status="Demo fixture service available",
            evaluation_status="Model evaluation pending",
            is_demo_data=True,
        )

    @staticmethod
    def _empty_snapshot() -> CommandCenterSnapshot:
        from ..models import PredictionResponse

        return CommandCenterSnapshot(
            rows=[],
            kpis=CommandCenterKpis(
                predictions_analyzed=0,
                high_risk_customers=0,
                average_predicted_risk=None,
                recent_high_risk_share=None,
            ),
            distribution=RiskDistribution(low=0, medium=0, high=0, threshold=0.5),
            review_items=[],
            model_version="demo-fixture-v1.0.0",
            generated_at=PredictionResponse.demo_timestamp(),
            service_status="Demo fixture service available",
            evaluation_status="Model evaluation pending",
            is_demo_data=True,
        )
