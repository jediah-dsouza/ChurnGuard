from __future__ import annotations

import csv
import io
from typing import Literal

from pydantic import ValidationError

from ..models import (
    BatchResult,
    BatchSummary,
    BatchValidationIssue,
    BatchValidationResult,
    CustomerInput,
    PredictionHistoryRow,
    PredictionRequest,
    RiskLabel,
)
from .contract import BatchServiceError, PredictionServiceError
from .mock_prediction import MockPredictionService


DemoBatchMode = Literal["valid", "invalid", "empty", "malformed"]


class MockBatchService:
    """Deterministic batch adapter over the approved customer fixtures."""

    def __init__(self, prediction_service: MockPredictionService | None = None) -> None:
        self._predictions = prediction_service or MockPredictionService()

    @staticmethod
    def schema_columns() -> list[str]:
        return [
            field.alias or name
            for name, field in CustomerInput.model_fields.items()
        ]

    def demo_csv(self) -> bytes:
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=self.schema_columns())
        writer.writeheader()
        for fixture in self._predictions.fixtures():
            fixture_id = fixture.get("fixtureId")
            if not isinstance(fixture_id, str):
                raise BatchServiceError("The demo batch could not be prepared.")
            writer.writerow(
                self._predictions.customer_for(fixture_id).model_dump(by_alias=True)
            )
        return buffer.getvalue().encode("utf-8")

    def validate_demo(
        self,
        mode: DemoBatchMode = "valid",
    ) -> BatchValidationResult:
        if mode == "empty":
            content = (",".join(self.schema_columns()) + "\n").encode("utf-8")
            return self.validate_csv(content, "approved-demo-batch.csv")
        if mode == "malformed":
            return self.validate_csv(b"\xff\xfe\x00", "approved-demo-batch.csv")

        content = self.demo_csv()
        if mode == "invalid":
            rows = list(csv.DictReader(content.decode("utf-8").splitlines()))
            rows[0]["customerID"] = ""
            rows[0]["tenure"] = ""
            buffer = io.StringIO()
            writer = csv.DictWriter(buffer, fieldnames=self.schema_columns())
            writer.writeheader()
            writer.writerows(rows)
            content = buffer.getvalue().encode("utf-8")
        return self.validate_csv(content, "approved-demo-batch.csv")

    def validate_csv(
        self,
        content: bytes,
        filename: str,
    ) -> BatchValidationResult:
        try:
            text = content.decode("utf-8-sig")
        except UnicodeDecodeError:
            return self._malformed(filename, "The file is not valid UTF-8 CSV.")

        try:
            reader = csv.DictReader(io.StringIO(text), strict=True)
            headers = reader.fieldnames
            if not headers:
                return self._malformed(filename, "The CSV header could not be read.")
            rows = list(reader)
        except (csv.Error, TypeError):
            return self._malformed(
                filename,
                "The file could not be interpreted as CSV.",
            )

        required = self.schema_columns()
        missing = [column for column in required if column not in headers]
        if missing:
            return BatchValidationResult(
                status="invalid",
                source_name=filename,
                total_records=len(rows),
                valid_records=0,
                invalid_records=len(rows),
                customers=[],
                issues=[
                    BatchValidationIssue(
                        message="Missing required columns: " + ", ".join(missing)
                    )
                ],
                preview_rows=self._preview(rows),
                is_demo_data=True,
            )
        if not rows:
            return BatchValidationResult(
                status="empty",
                source_name=filename,
                total_records=0,
                valid_records=0,
                invalid_records=0,
                customers=[],
                issues=[
                    BatchValidationIssue(
                        message="The dataset contains a header but no customer records."
                    )
                ],
                preview_rows=[],
                is_demo_data=True,
            )

        customers: list[CustomerInput] = []
        issues: list[BatchValidationIssue] = []
        for row_number, row in enumerate(rows, start=2):
            customer_id = (row.get("customerID") or "").strip() or None
            try:
                payload = {column: row.get(column) for column in required}
                if payload.get("SeniorCitizen") in {"0", "1"}:
                    payload["SeniorCitizen"] = int(payload["SeniorCitizen"])  # type: ignore[arg-type]
                customer = CustomerInput.model_validate(payload)
                canonical = self._predictions.customer_for(customer.customer_id)
                if customer != canonical:
                    raise PredictionServiceError(
                        "Values do not match the approved deterministic fixture."
                    )
            except ValidationError:
                issues.append(
                    BatchValidationIssue(
                        row_number=row_number,
                        customer_id=customer_id,
                        message="Required or typed customer fields are invalid.",
                    )
                )
            except PredictionServiceError:
                issues.append(
                    BatchValidationIssue(
                        row_number=row_number,
                        customer_id=customer_id,
                        message=(
                            "Customer values do not match an approved deterministic fixture."
                        ),
                    )
                )
            else:
                customers.append(customer)

        return BatchValidationResult(
            status="invalid" if issues else "valid",
            source_name=filename,
            total_records=len(rows),
            valid_records=len(customers),
            invalid_records=len(issues),
            customers=customers,
            issues=issues,
            preview_rows=self._preview(rows),
            is_demo_data=True,
        )

    def analyze(
        self,
        validation: BatchValidationResult,
        *,
        fail: bool = False,
    ) -> BatchResult:
        if validation.status != "valid" or not validation.customers:
            raise BatchServiceError(
                "Only a fully valid non-empty dataset can be analyzed."
            )
        if fail:
            raise BatchServiceError(
                "The demo batch service is temporarily unavailable."
            )

        rows: list[PredictionHistoryRow] = []
        for customer in validation.customers:
            try:
                prediction = self._predictions.predict(
                    PredictionRequest(customer=customer)
                )
            except PredictionServiceError as exc:
                raise BatchServiceError(
                    "The demo batch could not be analyzed."
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
        rows.sort(key=lambda row: (-row.risk_probability, row.customer_id))
        total = len(rows)
        return BatchResult(
            rows=rows,
            summary=BatchSummary(
                records_analyzed=total,
                high_risk=sum(row.risk_label == RiskLabel.HIGH for row in rows),
                medium_risk=sum(row.risk_label == RiskLabel.MEDIUM for row in rows),
                low_risk=sum(row.risk_label == RiskLabel.LOW for row in rows),
                average_predicted_risk=sum(
                    row.risk_probability for row in rows
                )
                / total,
            ),
            model_version=rows[0].model_version,
            generated_at=max(row.predicted_at for row in rows),
            is_demo_data=True,
        )

    @staticmethod
    def results_csv(result: BatchResult) -> bytes:
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(
            [
                "customerID",
                "riskProbability",
                "riskLabel",
                "topDriver",
                "tenure",
                "contract",
                "generatedAt",
                "modelVersion",
            ]
        )
        for row in result.rows:
            writer.writerow(
                [
                    row.customer_id,
                    f"{row.risk_probability:.2f}",
                    row.risk_label.value,
                    row.top_driver,
                    row.tenure,
                    row.contract,
                    row.predicted_at.isoformat(),
                    row.model_version,
                ]
            )
        return buffer.getvalue().encode("utf-8")

    @staticmethod
    def _preview(rows: list[dict[str, str | None]]) -> list[dict[str, str]]:
        columns = ["customerID", "tenure", "Contract", "MonthlyCharges"]
        return [
            {column: str(row.get(column) or "") for column in columns}
            for row in rows[:5]
        ]

    @staticmethod
    def _malformed(filename: str, message: str) -> BatchValidationResult:
        return BatchValidationResult(
            status="malformed",
            source_name=filename,
            total_records=0,
            valid_records=0,
            invalid_records=0,
            customers=[],
            issues=[BatchValidationIssue(message=message)],
            preview_rows=[],
            is_demo_data=True,
        )