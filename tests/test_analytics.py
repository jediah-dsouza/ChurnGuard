from datetime import date

import pytest
from streamlit.testing.v1 import AppTest

from frontend.streamlit_app.models import RiskLabel
from frontend.streamlit_app.services import (
    AnalyticsServiceError,
    MockAnalyticsService,
)


ANALYTICS_PATH = "frontend/streamlit_app/pages/analytics.py"


def test_analytics_snapshot_calculations_are_deterministic() -> None:
    snapshot = MockAnalyticsService().snapshot()
    assert snapshot.predictions_analyzed == 4
    assert snapshot.average_predicted_risk == pytest.approx(0.5275)
    assert snapshot.high_risk_rate == pytest.approx(0.5)
    assert snapshot.distribution.low == 1
    assert snapshot.distribution.medium == 1
    assert snapshot.distribution.high == 2
    assert snapshot.distribution.threshold == 0.5
    assert {
        row.customer_id: (row.risk_probability, row.risk_label)
        for row in snapshot.rows
    } == {
        "CUST-LOW-001": (0.11, RiskLabel.LOW),
        "CUST-HIGH-001": (0.87, RiskLabel.HIGH),
        "CUST-BORDERLINE-001": (0.52, RiskLabel.MEDIUM),
        "CUST-HARD-001": (0.61, RiskLabel.HIGH),
    }


def test_prediction_volume_uses_only_fixture_timestamp() -> None:
    snapshot = MockAnalyticsService().snapshot()
    assert len(snapshot.volume_over_time) == 1
    assert snapshot.volume_over_time[0].day == date(2026, 10, 4)
    assert snapshot.volume_over_time[0].prediction_count == 4


def test_contract_breakdown_is_sorted_by_average_risk() -> None:
    rows = MockAnalyticsService().snapshot("contract").segment_rows
    assert [row.segment_value for row in rows] == [
        "Month-to-month",
        "One year",
        "Two year",
    ]
    assert rows[0].customer_count == 2
    assert rows[0].average_predicted_risk == pytest.approx(0.695)
    assert rows[0].high_risk_count == 1
    assert rows[0].high_risk_share == pytest.approx(0.5)


def test_tenure_breakdown_uses_existing_operational_buckets() -> None:
    rows = MockAnalyticsService().snapshot("tenure_bucket").segment_rows
    assert {
        row.segment_value: (
            row.customer_count,
            row.average_predicted_risk,
            row.high_risk_count,
        )
        for row in rows
    } == {
        "0–12 months": (1, 0.87, 1),
        "13–36 months": (2, pytest.approx(0.565), 1),
        "37+ months": (1, 0.11, 0),
    }


def test_internet_and_payment_breakdowns_use_fixture_values() -> None:
    internet = MockAnalyticsService().snapshot("internet_service").segment_rows
    assert internet[0].segment_value == "Fiber optic"
    assert internet[0].customer_count == 3
    assert internet[0].average_predicted_risk == pytest.approx(2.0 / 3.0)
    assert internet[0].high_risk_count == 2

    payment = MockAnalyticsService().snapshot("payment_method").segment_rows
    assert payment[0].segment_value == "Electronic check"
    assert payment[0].customer_count == 2
    assert payment[0].average_predicted_risk == pytest.approx(0.74)
    assert payment[0].high_risk_share == pytest.approx(1.0)


def test_prediction_success_failure_is_honestly_unavailable() -> None:
    snapshot = MockAnalyticsService().snapshot()
    assert snapshot.prediction_outcomes_available is False
    assert "cannot be derived" in snapshot.prediction_outcomes_note


def test_empty_and_malformed_analytics_contracts() -> None:
    empty = MockAnalyticsService().snapshot(mode="empty")
    assert empty.rows == []
    assert empty.predictions_analyzed == 0
    assert empty.average_predicted_risk is None
    assert empty.high_risk_rate is None
    assert empty.volume_over_time == []
    assert empty.segment_rows == []

    with pytest.raises(AnalyticsServiceError, match="could not be prepared"):
        MockAnalyticsService().snapshot(mode="malformed")


def test_unknown_segment_is_rejected() -> None:
    with pytest.raises(AnalyticsServiceError, match="not supported"):
        MockAnalyticsService().snapshot("unsupported")  # type: ignore[arg-type]


def test_analytics_page_populated_state() -> None:
    app = AppTest.from_file(ANALYTICS_PATH, default_timeout=10).run()
    assert not app.exception
    page_text = " ".join(item.value for item in app.markdown)
    assert "Analytics snapshot measures" in page_text
    assert "52.8%" in page_text
    assert "50.0%" in page_text
    assert "Risk-band distribution" in page_text
    assert "04 Oct 2026" in page_text
    assert "Rate not available" in page_text
    assert "Month-to-month" in page_text


@pytest.mark.parametrize(
    ("selection", "expected"),
    [
        ("Tenure bucket", "0–12 months"),
        ("Internet service", "Fiber optic"),
        ("Payment method", "Electronic check"),
    ],
)
def test_analytics_page_segment_interactions(
    selection: str,
    expected: str,
) -> None:
    app = AppTest.from_file(ANALYTICS_PATH, default_timeout=10).run()
    app.selectbox(key="analytics_segment").select(selection).run()
    assert not app.exception
    assert expected in " ".join(item.value for item in app.markdown)


def test_analytics_page_empty_state() -> None:
    app = AppTest.from_file(ANALYTICS_PATH, default_timeout=10).run()
    app.selectbox(key="analytics_mode").select("Empty analytics").run()
    page_text = " ".join(item.value for item in app.markdown)
    assert "No analytics data available" in page_text
    assert "/app/predict" in page_text


def test_analytics_page_error_and_recovery() -> None:
    app = AppTest.from_file(ANALYTICS_PATH, default_timeout=10).run()
    app.selectbox(key="analytics_mode").select("Malformed analytics").run()
    assert "could not be loaded" in app.error[0].value
    retry = next(
        button for button in app.button if button.label == "Retry sample analytics"
    )
    retry.click().run()
    assert not app.error
    assert "Analytics snapshot measures" in " ".join(
        item.value for item in app.markdown
    )