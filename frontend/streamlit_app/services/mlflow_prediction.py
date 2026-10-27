
from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd

from ..models import (
    CustomerInput,
    Driver,
    DriverDirection,
    PredictionRequest,
    PredictionResponse,
    Recommendation,
    RecommendationPriority,
    RiskLabel,
)
from .contract import PredictionServiceError


MODEL_NAME = "ChurnGuard-XGBoost"
MODEL_VERSION = "1"
MODEL_THRESHOLD = 0.45
MAX_DRIVERS = 3

FEATURE_COLUMNS = [
    "gender",
    "SeniorCitizen",
    "Partner",
    "Dependents",
    "tenure",
    "PhoneService",
    "MultipleLines",
    "InternetService",
    "OnlineSecurity",
    "OnlineBackup",
    "DeviceProtection",
    "TechSupport",
    "StreamingTV",
    "StreamingMovies",
    "Contract",
    "PaperlessBilling",
    "PaymentMethod",
    "MonthlyCharges",
    "TotalCharges",
]


def _feature_label(name: str) -> str:
    """Convert transformed pipeline feature names into readable labels."""
    name = name.replace("num__", "").replace("cat__", "")
    name = name.replace("remainder__", "")
    name = name.replace("_", " ")

    replacements = {
        "SeniorCitizen": "Senior citizen",
        "MonthlyCharges": "Monthly charges",
        "TotalCharges": "Total charges",
        "PhoneService": "Phone service",
        "MultipleLines": "Multiple lines",
        "InternetService": "Internet service",
        "OnlineSecurity": "Online security",
        "OnlineBackup": "Online backup",
        "DeviceProtection": "Device protection",
        "TechSupport": "Technical support",
        "StreamingTV": "Streaming TV",
        "StreamingMovies": "Streaming movies",
        "PaperlessBilling": "Paperless billing",
        "PaymentMethod": "Payment method",
    }

    for original, label in replacements.items():
        name = name.replace(original, label)

    return name.strip()


class MLflowPredictionService:
    """Scores customers and generates best-effort SHAP explanations."""

    def __init__(self) -> None:
        tracking_uri = os.environ.get("MLFLOW_TRACKING_URI")

        if not tracking_uri:
            project_root = Path(__file__).resolve().parents[3]
            db_path = (
                project_root
                / "ml"
                / "reports"
                / "model_registry"
                / "mlflow.db"
            ).resolve().as_posix()

            tracking_uri = f"sqlite:///{db_path}"

        mlflow.set_tracking_uri(tracking_uri)

        try:
            self._model = mlflow.sklearn.load_model(
                f"models:/{MODEL_NAME}/{MODEL_VERSION}"
            )
        except Exception as exc:
            raise PredictionServiceError(
                "The registered ChurnGuard model could not be loaded. "
                "Check the MLflow tracking URI and model registration."
            ) from exc

        self._threshold = MODEL_THRESHOLD
        self._explainer = None
        self._explainer_error: str | None = None

    def _build_frame(self, customer: CustomerInput) -> pd.DataFrame:
        values = customer.model_dump(by_alias=True)
        values.pop("customerID", None)

        return pd.DataFrame(
            [{column: values[column] for column in FEATURE_COLUMNS}],
            columns=FEATURE_COLUMNS,
        )

    def _get_explainer(self):
        """Initialize the tree explainer once, when SHAP is available."""
        if self._explainer is not None:
            return self._explainer

        if self._explainer_error is not None:
            return None

        try:
            import shap

            if not hasattr(self._model, "named_steps"):
                raise TypeError(
                    "The registered model is not a supported sklearn pipeline."
                )

            estimator = self._model.named_steps["model"]

            self._explainer = shap.TreeExplainer(
                estimator,
                model_output="raw",
            )
            return self._explainer

        except Exception as exc:
            self._explainer_error = (
                f"{type(exc).__name__}: {exc}"
            )
            print(
                "[SHAP] Explainer unavailable: "
                f"{self._explainer_error}",
                flush=True,
            )
            return None

    def _explain(
        self,
        frame: pd.DataFrame,
        churn_index: int,
    ) -> list[Driver]:
        """Return the strongest SHAP contributions in raw model-output units."""
        try:
            preprocess = self._model.named_steps["preprocess"]
            transformed = preprocess.transform(frame)

            # Get readable names for the transformed features when supported.
            try:
                feature_names = list(
                    preprocess.get_feature_names_out()
                )
            except Exception:
                feature_names = [
                    f"Feature {index + 1}"
                    for index in range(transformed.shape[1])
                ]

            explainer = self._get_explainer()
            if explainer is None:
                return []

            raw_values = explainer.shap_values(transformed)

            # Some SHAP versions return a list containing one array per class.
            if isinstance(raw_values, list):
                if churn_index >= len(raw_values):
                    raise ValueError(
                        "SHAP did not return values for the churn class."
                    )
                values = np.asarray(raw_values[churn_index])
            else:
                values = np.asarray(raw_values)

                # Some versions return (samples, features, classes).
                if values.ndim == 3:
                    if churn_index >= values.shape[2]:
                        raise ValueError(
                            "SHAP did not return values for the churn class."
                        )
                    values = values[:, :, churn_index]

            if values.ndim != 2 or values.shape[0] != 1:
                raise ValueError(
                    f"Unexpected SHAP output shape: {values.shape}"
                )

            contributions = values[0]

            if len(contributions) != len(feature_names):
                raise ValueError(
                    "SHAP contributions do not match transformed features."
                )

            if not np.isfinite(contributions).all():
                raise ValueError(
                    "SHAP returned non-finite contribution values."
                )

            ranked_indices = np.argsort(
                np.abs(contributions)
            )[::-1][:MAX_DRIVERS]

            drivers: list[Driver] = []

            for index in ranked_indices:
                impact = float(contributions[index])

                if impact == 0:
                    continue

                direction = (
                    DriverDirection.INCREASES
                    if impact > 0
                    else DriverDirection.DECREASES
                )

                feature = _feature_label(feature_names[index])

                drivers.append(
                    Driver(
                        feature=feature,
                        direction=direction,
                        impact=impact,
                        explanation=(
                            f"SHAP contribution to the model's raw output "
                            f"(log-odds): {impact:+.4f}. "
                            + (
                                "This pushes the prediction toward churn."
                                if impact > 0
                                else "This pushes the prediction away from churn."
                            )
                        ),
                    )
                )

            return drivers

        except Exception as exc:
            print(
                "[SHAP] Could not explain prediction: "
                f"{type(exc).__name__}: {exc}",
                flush=True,
            )
            return []

    def predict(self, request: PredictionRequest) -> PredictionResponse:
        customer = request.customer
        frame = self._build_frame(customer)

        try:
            probabilities = self._model.predict_proba(frame)[0]
            classes = list(self._model.classes_)

            if 1 not in classes:
                raise ValueError("The model has no class labeled 1.")

            churn_index = classes.index(1)
            probability = float(probabilities[churn_index])

            if not np.isfinite(probability):
                raise ValueError("The model returned an invalid probability.")

        except Exception as exc:
            raise PredictionServiceError(
                "The registered model could not score these customer inputs."
            ) from exc

        is_high_risk = probability >= self._threshold

        if probability >= 0.65:
            risk_label = RiskLabel.HIGH
            priority = RecommendationPriority.HIGH
            summary = "Prioritize this customer for retention review."
            actions = [
                "Review contract and billing concerns with the customer.",
                "Check whether support or security needs remain unmet.",
                "Offer an appropriate retention option after confirming needs.",
            ]
        elif is_high_risk:
            risk_label = RiskLabel.MEDIUM
            priority = RecommendationPriority.MEDIUM
            summary = "Consider a proactive retention check-in."
            actions = [
                "Ask about the customer's current service experience.",
                "Review suitable contract and payment options.",
                "Monitor subsequent engagement and account changes.",
            ]
        else:
            risk_label = RiskLabel.LOW
            priority = RecommendationPriority.LOW
            summary = "Continue normal customer engagement."
            actions = [
                "Maintain regular customer communications.",
                "Monitor account changes and support needs.",
                "Reassess risk when new customer information is available.",
            ]

        # SHAP failure does not prevent the risk prediction from succeeding.
        drivers = self._explain(frame, churn_index)

        return PredictionResponse(
            predictionId=str(uuid4()),
            customerId=customer.customer_id,
            riskProbability=probability,
            riskLabel=risk_label,
            threshold=self._threshold,
            topDrivers=drivers,
            recommendation=Recommendation(
                priority=priority,
                summary=summary,
                actions=actions,
            ),
            generatedAt=datetime.now(timezone.utc),
            modelVersion=f"{MODEL_NAME}-v{MODEL_VERSION}",
            isDemoData=False,
            scenario="live_model_prediction",
            scenarioDescription=(
                "Scored by the registered ChurnGuard XGBoost pipeline. "
                "SHAP contributions are reported in raw model-output "
                "units and are not percentage-point changes in probability. "
                "The prediction is a model estimate, not a confirmed outcome."
            ),
        )
