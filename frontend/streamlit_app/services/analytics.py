from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from typing import Literal

from ..models import (
    AnalyticsSegmentRow,
    AnalyticsSnapshot,
    AnalyticsTimePoint,
    CustomerInput,
    PredictionHistoryRow,
    PredictionRequest,
    PredictionResponse,
    RiskDistribution,
    RiskLabel,
)
from .contract import AnalyticsServiceError
from .mock_prediction import MockPredictionService


AnalyticsMode = Literal["sample", "empty", "malformed"]
AnalyticsSegment = Literal[
    "contract",
    "tenure_bucket",
    "internet_service",
    "payment_method",
]


@dataclass(frozen=True)
class _AnalyticsRecord:
    customer: CustomerInput
    prediction: PredictionResponse
    row: PredictionHistoryRow


class MockAnalyticsService:
    """Derives an honest analytics snapshot from approved deterministic fixtures."""

    SEGMENT_LABELS: dict[AnalyticsSegment, str] = {
        "contract": "Contract",
        "tenure_bucket": "Tenure bucket",
        "internet_service": "Internet service",
        "payment_method": "Payment method",
    }

    def __init__(self, prediction_service: MockPredictionService | None = None) -> None:
        self._predictions = prediction_service or MockPredictionService()

    def snapshot(
        self,
        segment: AnalyticsSegment = "contract",
        *,
        mode: AnalyticsMode = "sample",
    ) -> AnalyticsSnapshot:
        if segment not in self.SEGMENT_LABELS:
            raise AnalyticsServiceError("The requested analytics segment is not supported.")
        if mode == "malformed":
            raise AnalyticsServiceError(
                "The demo analytics snapshot could not be prepared."
            )

        records = [] if mode == "empty" else self._load_records()
        rows = [record.row for record in records]
        total = len(rows)
        high_count = sum(row.risk_label == RiskLabel.HIGH for row in rows)
        average = (
            sum(row.risk_probability for row in rows) / total if total else None
        )
        high_rate = high_count / total if total else None
        volume_counts: dict[date, int] = defaultdict(int)
        for row in rows:
            volume_counts[row.predicted_at.date()] += 1
        volume = [
            AnalyticsTimePoint(day=day, prediction_count=count)
            for day, count in sorted(volume_counts.items())
        ]
        segment_rows = self._segment_rows(records, segment)

        return AnalyticsSnapshot(
            rows=rows,
            predictions_analyzed=total,
            average_predicted_risk=average,
            high_risk_rate=high_rate,
            distribution=RiskDistribution(
                low=sum(row.risk_label == RiskLabel.LOW for row in rows),
                medium=sum(row.risk_label == RiskLabel.MEDIUM for row in rows),
                high=high_count,
                threshold=rows[0].threshold if rows else 0.5,
            ),
            volume_over_time=volume,
            segment_dimension=self.SEGMENT_LABELS[segment],
            segment_rows=segment_rows,
            segment_insight=self._segment_insight(segment_rows),
            prediction_outcomes_available=False,
            prediction_outcomes_note=(
                "The approved fixtures store deterministic prediction results, "
                "but no prediction-attempt outcome log. A success/failure rate "
                "cannot be derived and is not inferred."
            ),
            model_version=rows[0].model_version if rows else "demo-fixture-v1.0.0",
            generated_at=(
                max(row.predicted_at for row in rows)
                if rows
                else PredictionResponse.demo_timestamp()
            ),
            service_status="Demo fixture service available",
            is_demo_data=True,
        )

    def _load_records(self) -> list[_AnalyticsRecord]:
        records: list[_AnalyticsRecord] = []
        for fixture in self._predictions.fixtures():
            fixture_id = fixture.get("fixtureId")
            if not isinstance(fixture_id, str):
                raise AnalyticsServiceError(
                    "The demo analytics snapshot contains an invalid customer record."
                )
            try:
                customer = self._predictions.customer_for(fixture_id)
                prediction = self._predictions.predict(
                    PredictionRequest(customer=customer)
                )
            except Exception as exc:
                raise AnalyticsServiceError(
                    "The demo analytics snapshot could not be prepared."
                ) from exc
            records.append(
                _AnalyticsRecord(
                    customer=customer,
                    prediction=prediction,
                    row=PredictionHistoryRow(
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
                    ),
                )
            )
        return records

    @staticmethod
    def _segment_value(record: _AnalyticsRecord, segment: AnalyticsSegment) -> str:
        customer = record.customer
        if segment == "contract":
            return customer.contract
        if segment == "internet_service":
            return customer.internet_service
        if segment == "payment_method":
            return customer.payment_method
        if customer.tenure <= 12:
            return "0–12 months"
        if customer.tenure <= 36:
            return "13–36 months"
        return "37+ months"

    def _segment_rows(
        self,
        records: list[_AnalyticsRecord],
        segment: AnalyticsSegment,
    ) -> list[AnalyticsSegmentRow]:
        groups: dict[str, list[_AnalyticsRecord]] = defaultdict(list)
        for record in records:
            groups[self._segment_value(record, segment)].append(record)

        rows = []
        for value, grouped in groups.items():
            count = len(grouped)
            high_count = sum(
                item.prediction.risk_label == RiskLabel.HIGH for item in grouped
            )
            rows.append(
                AnalyticsSegmentRow(
                    segment_value=value,
                    customer_count=count,
                    average_predicted_risk=sum(
                        item.prediction.risk_probability for item in grouped
                    )
                    / count,
                    high_risk_count=high_count,
                    high_risk_share=high_count / count,
                )
            )
        return sorted(
            rows,
            key=lambda row: (
                -row.average_predicted_risk,
                -row.customer_count,
                row.segment_value,
            ),
        )

    @staticmethod
    def _segment_insight(rows: list[AnalyticsSegmentRow]) -> str | None:
        if not rows:
            return None
        leader = rows[0]
        customer_word = "customer" if leader.customer_count == 1 else "customers"
        return (
            f"{leader.segment_value} has the highest average demo risk at "
            f"{leader.average_predicted_risk * 100:.1f}% across "
            f"{leader.customer_count} {customer_word}; "
            f"{leader.high_risk_count} are labeled High."
        )