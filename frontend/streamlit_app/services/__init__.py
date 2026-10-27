"""Prediction service implementations."""

from .contract import (
    AnalyticsService,
    AnalyticsServiceError,
    BatchService,
    BatchServiceError,
    ExplanationDataError,
    ExplanationNotFound,
    ExplanationService,
    ExplanationServiceError,
    ModelService,
    ModelServiceError,
    PredictionService,
    PredictionServiceError,
)
from .analytics import MockAnalyticsService
from .explanations import MockExplanationService
from .model import MockModelService
from .command_center import CommandCenterDataError, MockCommandCenterService
from .customer_history import (
    CustomerHistoryDataError,
    CustomerHistoryQuery,
    MockCustomerHistoryService,
)
from .customer_detail import (
    CustomerDetailDataError,
    CustomerDetailNotFound,
    MockCustomerDetailService,
)
from .mock_prediction import MockPredictionService
from .mock_batch import MockBatchService

__all__ = [
    "AnalyticsService",
    "AnalyticsServiceError",
    "ExplanationDataError",
    "ExplanationNotFound",
    "ExplanationService",
    "ExplanationServiceError",
    "CommandCenterDataError",
    "BatchService",
    "BatchServiceError",
    "CustomerHistoryDataError",
    "CustomerHistoryQuery",
    "CustomerDetailDataError",
    "CustomerDetailNotFound",
    "MockCommandCenterService",
    "MockAnalyticsService",
    "MockModelService",
    "MockExplanationService",
    "MockCustomerDetailService",
    "MockCustomerHistoryService",
    "MockPredictionService",
    "MockBatchService",
    "PredictionService",
    "PredictionServiceError",
    "ModelService",
    "ModelServiceError",
]
