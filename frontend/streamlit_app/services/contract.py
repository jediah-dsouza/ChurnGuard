from __future__ import annotations

from typing import Protocol

from ..models import (
    AnalyticsSnapshot,
    BatchResult,
    BatchValidationResult,
    GlobalExplanationResult,
    LocalExplanationResult,
    ModelSnapshot,
    PredictionRequest,
    PredictionResponse,
    ServiceCapabilities,
)


class PredictionServiceError(RuntimeError):
    """Recoverable prediction-service failure safe to present to the UI."""


class PredictionService(Protocol):
    @property
    def capabilities(self) -> ServiceCapabilities: ...

    def predict(self, request: PredictionRequest) -> PredictionResponse: ...


class BatchServiceError(RuntimeError):
    """Recoverable batch-service failure safe to present to the UI."""


class BatchService(Protocol):
    def validate_demo(self, mode: str = "valid") -> BatchValidationResult: ...

    def validate_csv(self, content: bytes, filename: str) -> BatchValidationResult: ...

    def analyze(
        self,
        validation: BatchValidationResult,
        *,
        fail: bool = False,
    ) -> BatchResult: ...


class AnalyticsServiceError(RuntimeError):
    """Recoverable analytics-service failure safe to present to the UI."""


class AnalyticsService(Protocol):
    def snapshot(
        self,
        segment: str = "contract",
        *,
        mode: str = "sample",
    ) -> AnalyticsSnapshot: ...


class ModelServiceError(RuntimeError):
    """Recoverable model-metadata failure safe to present to the UI."""


class ModelService(Protocol):
    def snapshot(self, *, mode: str = "demo") -> ModelSnapshot: ...


class ExplanationServiceError(RuntimeError):
    """Recoverable explanation-service failure safe to present to the UI."""


class ExplanationDataError(RuntimeError):
    """Malformed explanation data safe to present without implementation detail."""


class ExplanationNotFound(LookupError):
    """The requested deterministic customer explanation does not exist."""


class ExplanationService(Protocol):
    def global_explanation(
        self,
        *,
        mode: str = "sample",
    ) -> GlobalExplanationResult: ...

    def local_explanation(
        self,
        customer_id: str,
        *,
        mode: str = "sample",
    ) -> LocalExplanationResult: ...
