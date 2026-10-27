from __future__ import annotations

from datetime import date, datetime, timezone
from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


YesNo = Literal["Yes", "No"]
InternetService = Literal["DSL", "Fiber optic", "No"]
Contract = Literal["Month-to-month", "One year", "Two year"]
PaymentMethod = Literal[
    "Electronic check",
    "Mailed check",
    "Bank transfer (automatic)",
    "Credit card (automatic)",
]


class RiskLabel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class DriverDirection(str, Enum):
    INCREASES = "increases_risk"
    DECREASES = "decreases_risk"


class RecommendationPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class CustomerInput(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    customer_id: str = Field(alias="customerID", min_length=1, max_length=64)
    gender: Literal["Female", "Male"]
    senior_citizen: Literal[0, 1] = Field(alias="SeniorCitizen")
    partner: YesNo = Field(alias="Partner")
    dependents: YesNo = Field(alias="Dependents")
    tenure: int = Field(ge=0, le=120)
    phone_service: YesNo = Field(alias="PhoneService")
    multiple_lines: YesNo = Field(alias="MultipleLines")
    internet_service: InternetService = Field(alias="InternetService")
    online_security: YesNo = Field(alias="OnlineSecurity")
    online_backup: YesNo = Field(alias="OnlineBackup")
    device_protection: YesNo = Field(alias="DeviceProtection")
    tech_support: YesNo = Field(alias="TechSupport")
    streaming_tv: YesNo = Field(alias="StreamingTV")
    streaming_movies: YesNo = Field(alias="StreamingMovies")
    contract: Contract = Field(alias="Contract")
    paperless_billing: YesNo = Field(alias="PaperlessBilling")
    payment_method: PaymentMethod = Field(alias="PaymentMethod")
    monthly_charges: float = Field(alias="MonthlyCharges", ge=0, le=1000)
    total_charges: float = Field(alias="TotalCharges", ge=0, le=100000)

    @field_validator("customer_id")
    @classmethod
    def customer_id_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Customer ID is required.")
        return value.strip()


class PredictionRequest(BaseModel):
    customer: CustomerInput
    schema_version: str = "1.0.0"


class Driver(BaseModel):
    feature: str
    direction: DriverDirection
    impact: float
    explanation: str


class Recommendation(BaseModel):
    priority: RecommendationPriority
    summary: str
    actions: list[str]


class PredictionResponse(BaseModel):
    prediction_id: str = Field(alias="predictionId")
    customer_id: str = Field(alias="customerId")
    risk_probability: float = Field(alias="riskProbability", ge=0, le=1)
    risk_label: RiskLabel = Field(alias="riskLabel")
    threshold: float = Field(ge=0, le=1)
    top_drivers: list[Driver] = Field(alias="topDrivers", min_length=3, max_length=3)
    recommendation: Recommendation
    generated_at: datetime = Field(alias="generatedAt")
    model_version: str = Field(alias="modelVersion")
    is_demo_data: bool = Field(alias="isDemoData")
    scenario: str
    scenario_description: str = Field(alias="scenarioDescription")

    @classmethod
    def demo_timestamp(cls) -> datetime:
        return datetime(2026, 10, 4, 18, 52, tzinfo=timezone.utc)


class ServiceCapabilities(BaseModel):
    transport: Literal["local-demo", "http"]
    requires_authentication: bool


class PredictionHistoryRow(BaseModel):
    customer_id: str
    risk_probability: float = Field(ge=0, le=1)
    risk_label: RiskLabel
    top_driver: str
    tenure: int
    contract: Contract
    predicted_at: datetime
    model_version: str
    threshold: float = Field(ge=0, le=1)
    scenario: str


class CommandCenterKpis(BaseModel):
    predictions_analyzed: int = Field(ge=0)
    high_risk_customers: int = Field(ge=0)
    average_predicted_risk: float | None = Field(default=None, ge=0, le=1)
    recent_high_risk_share: float | None = Field(default=None, ge=0, le=1)


class RiskDistribution(BaseModel):
    low: int = Field(ge=0)
    medium: int = Field(ge=0)
    high: int = Field(ge=0)
    threshold: float | None = Field(default=None, ge=0, le=1)


class ReviewItem(BaseModel):
    reference: str
    category: Literal["prediction", "input", "service"]
    title: str
    detail: str
    action: str


class CommandCenterSnapshot(BaseModel):
    rows: list[PredictionHistoryRow]
    kpis: CommandCenterKpis
    distribution: RiskDistribution
    review_items: list[ReviewItem]
    model_version: str
    generated_at: datetime
    service_status: str
    evaluation_status: str
    is_demo_data: bool


class CustomerHistoryResult(BaseModel):
    rows: list[PredictionHistoryRow]
    total_count: int = Field(ge=0)
    filtered_count: int = Field(ge=0)
    available_contracts: list[Contract]
    available_dates: list[date]
    model_version: str
    generated_at: datetime
    service_status: str
    is_demo_data: bool


class CustomerDetailResult(BaseModel):
    customer: CustomerInput
    prediction: PredictionResponse
    driver_values: list[str | None] = Field(min_length=3, max_length=3)
    service_status: str


class BatchValidationIssue(BaseModel):
    row_number: int | None = Field(default=None, ge=1)
    customer_id: str | None = None
    message: str


class BatchValidationResult(BaseModel):
    status: Literal["valid", "invalid", "empty", "malformed"]
    source_name: str
    total_records: int = Field(ge=0)
    valid_records: int = Field(ge=0)
    invalid_records: int = Field(ge=0)
    customers: list[CustomerInput]
    issues: list[BatchValidationIssue]
    preview_rows: list[dict[str, str]]
    is_demo_data: bool


class BatchSummary(BaseModel):
    records_analyzed: int = Field(ge=0)
    high_risk: int = Field(ge=0)
    medium_risk: int = Field(ge=0)
    low_risk: int = Field(ge=0)
    average_predicted_risk: float = Field(ge=0, le=1)


class BatchResult(BaseModel):
    rows: list[PredictionHistoryRow]
    summary: BatchSummary
    model_version: str
    generated_at: datetime
    is_demo_data: bool


class AnalyticsTimePoint(BaseModel):
    day: date
    prediction_count: int = Field(ge=0)


class AnalyticsSegmentRow(BaseModel):
    segment_value: str
    customer_count: int = Field(ge=0)
    average_predicted_risk: float = Field(ge=0, le=1)
    high_risk_count: int = Field(ge=0)
    high_risk_share: float = Field(ge=0, le=1)


class AnalyticsSnapshot(BaseModel):
    rows: list[PredictionHistoryRow]
    predictions_analyzed: int = Field(ge=0)
    average_predicted_risk: float | None = Field(default=None, ge=0, le=1)
    high_risk_rate: float | None = Field(default=None, ge=0, le=1)
    distribution: RiskDistribution
    volume_over_time: list[AnalyticsTimePoint]
    segment_dimension: str
    segment_rows: list[AnalyticsSegmentRow]
    segment_insight: str | None = None
    prediction_outcomes_available: bool
    prediction_outcomes_note: str
    model_version: str
    generated_at: datetime
    service_status: str
    is_demo_data: bool


class ModelCandidateRow(BaseModel):
    name: str
    status: Literal["planned"]
    accuracy: float | None = Field(default=None, ge=0, le=1)
    precision: float | None = Field(default=None, ge=0, le=1)
    recall: float | None = Field(default=None, ge=0, le=1)
    f1: float | None = Field(default=None, ge=0, le=1)
    roc_auc: float | None = Field(default=None, ge=0, le=1)
    pr_auc: float | None = Field(default=None, ge=0, le=1)


class ModelSnapshot(BaseModel):
    status: Literal["demo", "unavailable"]
    selected_model: str | None = None
    model_family: str | None = None
    model_version: str | None = None
    training_date: date | None = None
    experiment_tag: str | None = None
    feature_count: int | None = Field(default=None, ge=0)
    engineered_feature_count: int | None = Field(default=None, ge=0)
    minimum_engineered_features: int = Field(ge=0)
    training_data_description: str
    threshold: float | None = Field(default=None, ge=0, le=1)
    threshold_context: str
    calibration_status: str
    serialization_status: str
    serialization_formats: list[str]
    mlflow_experiment_reference: str | None = None
    mlflow_status: str
    candidates: list[ModelCandidateRow]
    fixture_service_available: bool
    service_status: str
    is_demo_data: bool


class ExplanationDriverItem(BaseModel):
    rank: int = Field(ge=1, le=3)
    feature: str
    family: str
    direction: DriverDirection
    demo_contribution: float
    explanation: str
    supporting_value: str | None = None


class GlobalExplanationDriver(BaseModel):
    rank: int = Field(ge=1)
    family: str
    direction: Literal["higher", "lower", "mixed"]
    relative_influence: str
    observed_count: int = Field(ge=1)
    meaning: str
    bar_percent: float = Field(ge=0, le=100)


class GlobalExplanationResult(BaseModel):
    status: Literal["populated", "empty", "unavailable"]
    drivers: list[GlobalExplanationDriver]
    sample_size: int = Field(ge=0)
    methodology_note: str
    is_demo_data: bool


class LocalExplanationResult(BaseModel):
    status: Literal["populated", "unavailable"]
    customer_id: str
    risk_probability: float = Field(ge=0, le=1)
    risk_label: RiskLabel
    threshold: float = Field(ge=0, le=1)
    drivers: list[ExplanationDriverItem]
    balancing_factors: list[ExplanationDriverItem]
    conflicting_signals: bool
    plain_english_summary: str
    operator_readout: str | None = None
    actions: list[str]
    model_version: str
    explanation_status: str
    is_demo_data: bool
