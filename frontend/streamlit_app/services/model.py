from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from ..models import (
    ModelCandidateRow,
    ModelSnapshot,
    PredictionRequest,
)
from .contract import ModelServiceError
from .mock_prediction import MockPredictionService


ModelMode = Literal["demo", "unavailable", "malformed"]


class MockModelService:
    """Builds honest model status from approved fixtures and project requirements."""

    def __init__(
        self,
        prediction_service: MockPredictionService | None = None,
        specification_path: Path | None = None,
    ) -> None:
        project_root = Path(__file__).resolve().parents[3]
        self._predictions = prediction_service or MockPredictionService()
        self._specification_path = (
            specification_path
            or project_root / "ChurnGuard_Master_JSON_Prompt.json"
        )

    def snapshot(self, *, mode: ModelMode = "demo") -> ModelSnapshot:
        if mode == "malformed":
            raise ModelServiceError(
                "The demo model metadata could not be prepared."
            )
        specification = self._load_specification()
        pipeline = specification.get("ml_pipeline")
        if not isinstance(pipeline, dict):
            raise ModelServiceError(
                "The project model requirements have an invalid format."
            )

        feature_engineering = pipeline.get("feature_engineering")
        serialization = pipeline.get("serialization")
        candidate_models = pipeline.get("candidate_models")
        dataset = pipeline.get("dataset")
        if (
            not isinstance(feature_engineering, dict)
            or not isinstance(serialization, dict)
            or not isinstance(candidate_models, list)
            or not all(isinstance(item, str) for item in candidate_models)
            or not isinstance(dataset, str)
        ):
            raise ModelServiceError(
                "The project model requirements have an invalid format."
            )

        minimum_engineered = feature_engineering.get(
            "minimum_engineered_features"
        )
        formats = serialization.get("formats")
        if (
            not isinstance(minimum_engineered, int)
            or not isinstance(formats, list)
            or not all(isinstance(item, str) for item in formats)
        ):
            raise ModelServiceError(
                "The project model requirements have an invalid format."
            )

        model_version: str | None = None
        threshold: float | None = None
        fixture_available = mode == "demo"
        if fixture_available:
            model_version, threshold = self._fixture_contract()

        candidates = [
            ModelCandidateRow(
                name=(
                    "Majority baseline"
                    if item == "Majority-class baseline"
                    else item
                ),
                status="planned",
            )
            for item in candidate_models
        ]
        return ModelSnapshot(
            status="demo" if fixture_available else "unavailable",
            selected_model=None,
            model_family=None,
            model_version=model_version,
            training_date=None,
            experiment_tag=None,
            feature_count=None,
            engineered_feature_count=None,
            minimum_engineered_features=minimum_engineered,
            training_data_description=dataset,
            threshold=threshold,
            threshold_context=(
                "A fixed marker from the deterministic fixture contract. It has "
                "not been selected or optimized through model evaluation."
                if threshold is not None
                else "No operating threshold is available because no model or "
                "fixture contract is connected."
            ),
            calibration_status="Not evaluated — no trained model results exist.",
            serialization_status="No serialized model artifact exists.",
            serialization_formats=list(formats),
            mlflow_experiment_reference=None,
            mlflow_status="No MLflow experiment is connected.",
            candidates=candidates,
            fixture_service_available=fixture_available,
            service_status=(
                "Deterministic fixture contract available"
                if fixture_available
                else "Model information unavailable"
            ),
            is_demo_data=True,
        )

    def _fixture_contract(self) -> tuple[str, float]:
        versions: set[str] = set()
        thresholds: set[float] = set()
        for fixture in self._predictions.fixtures():
            fixture_id = fixture.get("fixtureId")
            if not isinstance(fixture_id, str):
                raise ModelServiceError(
                    "The demo model metadata contains an invalid fixture record."
                )
            try:
                customer = self._predictions.customer_for(fixture_id)
                prediction = self._predictions.predict(
                    PredictionRequest(customer=customer)
                )
            except Exception as exc:
                raise ModelServiceError(
                    "The demo model metadata could not be prepared."
                ) from exc
            versions.add(prediction.model_version)
            thresholds.add(prediction.threshold)
        if len(versions) != 1 or len(thresholds) != 1:
            raise ModelServiceError(
                "The demo model metadata is inconsistent across fixtures."
            )
        return versions.pop(), thresholds.pop()

    def _load_specification(self) -> dict[str, object]:
        try:
            document = json.loads(
                self._specification_path.read_text(encoding="utf-8")
            )
        except (OSError, json.JSONDecodeError) as exc:
            raise ModelServiceError(
                "The project model requirements could not be loaded."
            ) from exc
        if not isinstance(document, dict):
            raise ModelServiceError(
                "The project model requirements have an invalid format."
            )
        return document