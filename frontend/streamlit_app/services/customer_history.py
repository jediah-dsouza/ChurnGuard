from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Literal

from ..models import (
    Contract,
    CustomerHistoryResult,
    PredictionHistoryRow,
    PredictionRequest,
    PredictionResponse,
    RiskLabel,
)
from .mock_prediction import MockPredictionService


TenureBucket = Literal["all", "0-12", "13-36", "37+"]
HistorySort = Literal["risk_desc", "risk_asc", "newest", "oldest"]
CustomerHistoryMode = Literal["sample", "empty", "malformed"]


class CustomerHistoryDataError(RuntimeError):
    """Safe customer-history failure for the recoverable UI state."""


@dataclass(frozen=True)
class CustomerHistoryQuery:
    search: str = ""
    risk: RiskLabel | None = None
    contract: Contract | None = None
    tenure_bucket: TenureBucket = "all"
    prediction_date: date | None = None
    sort: HistorySort = "risk_desc"


class MockCustomerHistoryService:
    """Queries approved prediction fixtures without leaking logic into the UI."""

    def __init__(self, prediction_service: MockPredictionService | None = None) -> None:
        self._predictions = prediction_service or MockPredictionService()

    def query(
        self,
        query: CustomerHistoryQuery | None = None,
        *,
        mode: CustomerHistoryMode = "sample",
    ) -> CustomerHistoryResult:
        active_query = query or CustomerHistoryQuery()
        if mode == "malformed":
            raise CustomerHistoryDataError(
                "The demo customer history could not be prepared."
            )

        all_rows = [] if mode == "empty" else self._load_rows()
        available_contracts = sorted({row.contract for row in all_rows})
        available_dates = sorted({row.predicted_at.date() for row in all_rows})
        rows = self._sort(self._filter(all_rows, active_query), active_query.sort)
        model_version = (
            all_rows[0].model_version if all_rows else "demo-fixture-v1.0.0"
        )
        generated_at = (
            max(row.predicted_at for row in all_rows)
            if all_rows
            else PredictionResponse.demo_timestamp()
        )
        return CustomerHistoryResult(
            rows=rows,
            total_count=len(all_rows),
            filtered_count=len(rows),
            available_contracts=available_contracts,
            available_dates=available_dates,
            model_version=model_version,
            generated_at=generated_at,
            service_status="Demo fixture service available",
            is_demo_data=True,
        )

    def _load_rows(self) -> list[PredictionHistoryRow]:
        rows: list[PredictionHistoryRow] = []
        for fixture in self._predictions.fixtures():
            fixture_id = fixture.get("fixtureId")
            if not isinstance(fixture_id, str):
                raise CustomerHistoryDataError(
                    "The demo customer history contains an invalid customer record."
                )
            try:
                customer = self._predictions.customer_for(fixture_id)
                prediction = self._predictions.predict(
                    PredictionRequest(customer=customer)
                )
            except Exception as exc:
                raise CustomerHistoryDataError(
                    "The demo customer history could not be prepared."
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
        return rows

    @staticmethod
    def _filter(
        rows: list[PredictionHistoryRow],
        query: CustomerHistoryQuery,
    ) -> list[PredictionHistoryRow]:
        search = query.search.strip().casefold()
        filtered: list[PredictionHistoryRow] = []
        for row in rows:
            searchable = " ".join(
                [
                    row.customer_id,
                    row.top_driver,
                    row.contract,
                    row.scenario.replace("_", " "),
                ]
            ).casefold()
            if search and search not in searchable:
                continue
            if query.risk is not None and row.risk_label != query.risk:
                continue
            if query.contract is not None and row.contract != query.contract:
                continue
            if not MockCustomerHistoryService._matches_tenure(
                row.tenure, query.tenure_bucket
            ):
                continue
            if (
                query.prediction_date is not None
                and row.predicted_at.date() != query.prediction_date
            ):
                continue
            filtered.append(row)
        return filtered

    @staticmethod
    def _matches_tenure(tenure: int, bucket: TenureBucket) -> bool:
        # Fixed operational buckets: first year, established years 2–3, long tenure.
        if bucket == "0-12":
            return 0 <= tenure <= 12
        if bucket == "13-36":
            return 13 <= tenure <= 36
        if bucket == "37+":
            return tenure >= 37
        return True

    @staticmethod
    def _sort(
        rows: list[PredictionHistoryRow],
        sort: HistorySort,
    ) -> list[PredictionHistoryRow]:
        if sort == "risk_asc":
            return sorted(rows, key=lambda row: (row.risk_probability, row.customer_id))
        if sort == "newest":
            return sorted(
                rows, key=lambda row: (-row.predicted_at.timestamp(), row.customer_id)
            )
        if sort == "oldest":
            return sorted(
                rows, key=lambda row: (row.predicted_at.timestamp(), row.customer_id)
            )
        return sorted(rows, key=lambda row: (-row.risk_probability, row.customer_id))