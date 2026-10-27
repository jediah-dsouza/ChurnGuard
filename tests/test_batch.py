import csv
import io

import pytest
from streamlit.testing.v1 import AppTest

from frontend.streamlit_app.models import RiskLabel
from frontend.streamlit_app.services import BatchServiceError, MockBatchService


BATCH_PATH = "frontend/streamlit_app/pages/batch.py"


def click_button(app: AppTest, label: str) -> AppTest:
    button = next(item for item in app.button if item.label == label)
    return button.click().run()


def load_valid_demo(app: AppTest) -> AppTest:
    app.selectbox(key="batch_source").select("Approved demo batch").run()
    return click_button(app, "Load and validate demo batch")


def test_batch_initial_state_has_no_dataset() -> None:
    app = AppTest.from_file(BATCH_PATH, default_timeout=10).run()
    assert not app.exception
    assert app.selectbox(key="batch_source").value is None
    assert "No dataset selected" in " ".join(item.value for item in app.markdown)


def test_valid_deterministic_batch_validation() -> None:
    validation = MockBatchService().validate_demo()
    assert validation.status == "valid"
    assert validation.total_records == 4
    assert validation.valid_records == 4
    assert validation.invalid_records == 0
    assert [customer.customer_id for customer in validation.customers] == [
        "CUST-LOW-001",
        "CUST-HIGH-001",
        "CUST-BORDERLINE-001",
        "CUST-HARD-001",
    ]


def test_invalid_deterministic_batch_reports_row_error() -> None:
    validation = MockBatchService().validate_demo("invalid")
    assert validation.status == "invalid"
    assert validation.total_records == 4
    assert validation.valid_records == 3
    assert validation.invalid_records == 1
    assert validation.issues[0].row_number == 2
    assert "invalid" in validation.issues[0].message


def test_empty_dataset_is_not_valid() -> None:
    validation = MockBatchService().validate_demo("empty")
    assert validation.status == "empty"
    assert validation.total_records == 0
    assert validation.customers == []
    assert "no customer records" in validation.issues[0].message


def test_malformed_dataset_is_safe() -> None:
    validation = MockBatchService().validate_demo("malformed")
    assert validation.status == "malformed"
    assert validation.total_records == 0
    assert "not valid UTF-8 CSV" in validation.issues[0].message


def test_missing_schema_columns_are_reported() -> None:
    validation = MockBatchService().validate_csv(
        b"customerID,tenure\nCUST-LOW-001,48\n",
        "missing-columns.csv",
    )
    assert validation.status == "invalid"
    assert validation.valid_records == 0
    assert "Missing required columns" in validation.issues[0].message


def test_uploaded_approved_csv_uses_only_fixture_records() -> None:
    service = MockBatchService()
    validation = service.validate_csv(service.demo_csv(), "upload.csv")
    assert validation.status == "valid"
    assert validation.source_name == "upload.csv"
    assert validation.is_demo_data is True


def test_edited_uploaded_customer_is_rejected() -> None:
    service = MockBatchService()
    rows = list(csv.DictReader(io.StringIO(service.demo_csv().decode("utf-8"))))
    rows[0]["MonthlyCharges"] = "999"
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=service.schema_columns())
    writer.writeheader()
    writer.writerows(rows)
    validation = service.validate_csv(output.getvalue().encode(), "edited.csv")
    assert validation.status == "invalid"
    assert validation.invalid_records == 1
    assert "approved deterministic fixture" in validation.issues[0].message


def test_batch_analysis_summary_and_prioritization() -> None:
    service = MockBatchService()
    result = service.analyze(service.validate_demo())
    assert result.summary.records_analyzed == 4
    assert result.summary.high_risk == 2
    assert result.summary.medium_risk == 1
    assert result.summary.low_risk == 1
    assert result.summary.average_predicted_risk == pytest.approx(0.5275)
    assert [row.customer_id for row in result.rows] == [
        "CUST-HIGH-001",
        "CUST-HARD-001",
        "CUST-BORDERLINE-001",
        "CUST-LOW-001",
    ]


def test_batch_results_preserve_fixture_predictions() -> None:
    result = MockBatchService().analyze(MockBatchService().validate_demo())
    actual = {
        row.customer_id: (row.risk_probability, row.risk_label)
        for row in result.rows
    }
    assert actual == {
        "CUST-LOW-001": (0.11, RiskLabel.LOW),
        "CUST-HIGH-001": (0.87, RiskLabel.HIGH),
        "CUST-BORDERLINE-001": (0.52, RiskLabel.MEDIUM),
        "CUST-HARD-001": (0.61, RiskLabel.HIGH),
    }


def test_invalid_or_empty_batch_cannot_run() -> None:
    service = MockBatchService()
    with pytest.raises(BatchServiceError, match="fully valid"):
        service.analyze(service.validate_demo("invalid"))
    with pytest.raises(BatchServiceError, match="fully valid"):
        service.analyze(service.validate_demo("empty"))


def test_batch_service_error_and_retry() -> None:
    service = MockBatchService()
    validation = service.validate_demo()
    with pytest.raises(BatchServiceError, match="temporarily unavailable"):
        service.analyze(validation, fail=True)
    recovered = service.analyze(validation)
    assert recovered.summary.records_analyzed == 4


def test_results_csv_contains_only_deterministic_results() -> None:
    service = MockBatchService()
    result = service.analyze(service.validate_demo())
    content = service.results_csv(result).decode("utf-8")
    assert "CUST-HIGH-001,0.87,High" in content
    assert "demo-fixture-v1.0.0" in content


def test_batch_page_validates_and_runs_demo_batch() -> None:
    app = AppTest.from_file(BATCH_PATH, default_timeout=10).run()
    app = load_valid_demo(app)
    page_text = " ".join(item.value for item in app.markdown)
    assert "Dataset ready" in page_text
    assert "approved-demo-batch.csv" in page_text
    app = click_button(app, "Run deterministic batch analysis")
    page_text = " ".join(item.value for item in app.markdown)
    assert "Batch result summary" in page_text
    assert "CUST-HIGH-001" in page_text
    assert "52.8%" in page_text
    assert any(
        button.label == "Inspect CUST-HIGH-001" for button in app.button
    )


@pytest.mark.parametrize(
    ("mode", "expected"),
    [
        ("Invalid approved batch", "Dataset blocked"),
        ("Empty approved batch", "Dataset is empty"),
        ("Malformed approved batch", "Dataset cannot be read"),
    ],
)
def test_batch_page_validation_states(mode: str, expected: str) -> None:
    app = AppTest.from_file(BATCH_PATH, default_timeout=10).run()
    app.selectbox(key="batch_demo_mode").select(mode).run()
    app.selectbox(key="batch_source").select("Approved demo batch").run()
    app = click_button(app, "Load and validate demo batch")
    assert expected in " ".join(item.value for item in app.markdown)
    run = next(
        item for item in app.button if item.label == "Run deterministic batch analysis"
    )
    assert run.disabled is True


def test_batch_page_recoverable_error_and_retry() -> None:
    app = AppTest.from_file(BATCH_PATH, default_timeout=10).run()
    app.checkbox(key="batch_force_failure").check().run()
    app = load_valid_demo(app)
    app = click_button(app, "Run deterministic batch analysis")
    assert "did not complete" in app.error[0].value
    app = click_button(app, "Retry batch analysis")
    assert not app.error
    assert "Batch result summary" in " ".join(
        item.value for item in app.markdown
    )


def test_batch_customer_inspection_preserves_selected_fixture() -> None:
    app = AppTest.from_file(BATCH_PATH, default_timeout=10).run()
    app = load_valid_demo(app)
    app = click_button(app, "Run deterministic batch analysis")
    app = click_button(app, "Inspect CUST-HIGH-001")
    assert not app.exception
    assert app.session_state["detail_route_fixture"] == "CUST-HIGH-001"