from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from time import sleep

from ..models import (
    CustomerInput,
    PredictionRequest,
    PredictionResponse,
    ServiceCapabilities,
)
from .contract import PredictionServiceError


class MockPredictionService:
    """Deterministic adapter over the approved frontend fixture file."""

    def __init__(
        self,
        data_path: Path | None = None,
        *,
        latency_seconds: float = 0.0,
        fail_next: bool = False,
    ) -> None:
        project_root = Path(__file__).resolve().parents[3]
        self._data_path = data_path or project_root / "CHURNGUARD_SAMPLE_DATA.json"
        self._latency_seconds = latency_seconds
        self._fail_next = fail_next
        self._document = self._load_document()

    @property
    def capabilities(self) -> ServiceCapabilities:
        return ServiceCapabilities(
            transport="local-demo",
            requires_authentication=False,
        )

    def _load_document(self) -> dict[str, object]:
        try:
            raw = json.loads(self._data_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise PredictionServiceError("Demo fixtures could not be loaded.") from exc
        if raw.get("isDemoData") is not True:
            raise PredictionServiceError("The fixture source is not marked as demo data.")
        return raw

    def fixtures(self) -> list[dict[str, object]]:
        return deepcopy(self._document["fixtures"])  # type: ignore[index]

    def customer_for(self, fixture_id: str) -> CustomerInput:
        fixture = self._fixture_for(fixture_id)
        return CustomerInput.model_validate(fixture["customer"])

    def _fixture_for(self, fixture_id: str) -> dict[str, object]:
        fixtures = self._document.get("fixtures")
        if not isinstance(fixtures, list):
            raise PredictionServiceError("Demo fixtures have an invalid format.")
        for fixture in fixtures:
            if isinstance(fixture, dict) and fixture.get("fixtureId") == fixture_id:
                return fixture
        raise PredictionServiceError(
            "This customer is not available in the deterministic demo set."
        )

    def predict(self, request: PredictionRequest) -> PredictionResponse:
        if self._latency_seconds:
            sleep(self._latency_seconds)
        if self._fail_next:
            self._fail_next = False
            raise PredictionServiceError(
                "The demo prediction service is temporarily unavailable."
            )

        fixture = self._fixture_for(request.customer.customer_id)
        canonical = CustomerInput.model_validate(fixture["customer"])
        if request.customer != canonical:
            raise PredictionServiceError(
                "Edited values do not match a deterministic demo fixture. "
                "Reset or load a sample customer to continue."
            )

        prediction = fixture["expectedDemoPrediction"]
        if not isinstance(prediction, dict):
            raise PredictionServiceError("The demo prediction has an invalid format.")
        payload = {
            **prediction,
            "customerId": request.customer.customer_id,
            "generatedAt": PredictionResponse.demo_timestamp(),
            "modelVersion": "demo-fixture-v1.0.0",
            "isDemoData": True,
            "scenario": fixture["scenario"],
            "scenarioDescription": fixture["description"],
        }
        return PredictionResponse.model_validate(payload)
