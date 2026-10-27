import pytest
from streamlit.testing.v1 import AppTest

from frontend.streamlit_app.services import (
    CommandCenterDataError,
    MockCommandCenterService,
)


COMMAND_CENTER_PATH = "frontend/streamlit_app/pages/command_center.py"


def test_command_center_snapshot_calculations() -> None:
    snapshot = MockCommandCenterService().snapshot()
    assert snapshot.kpis.predictions_analyzed == 4
    assert snapshot.kpis.high_risk_customers == 2
    assert snapshot.kpis.average_predicted_risk == pytest.approx(0.5275)
    assert snapshot.kpis.recent_high_risk_share == pytest.approx(0.5)
    assert snapshot.is_demo_data is True


def test_risk_distribution_uses_fixture_labels() -> None:
    distribution = MockCommandCenterService().snapshot().distribution
    assert distribution.low == 1
    assert distribution.medium == 1
    assert distribution.high == 2
    assert distribution.threshold == 0.5


def test_priority_queue_is_sorted_by_operational_priority() -> None:
    rows = MockCommandCenterService().snapshot().rows
    assert [row.customer_id for row in rows] == [
        "CUST-HIGH-001",
        "CUST-HARD-001",
        "CUST-BORDERLINE-001",
        "CUST-LOW-001",
    ]


def test_empty_history_is_explicit_and_has_no_fake_metrics() -> None:
    snapshot = MockCommandCenterService().snapshot("empty")
    assert snapshot.rows == []
    assert snapshot.kpis.predictions_analyzed == 0
    assert snapshot.kpis.average_predicted_risk is None
    assert snapshot.kpis.recent_high_risk_share is None


def test_malformed_history_uses_safe_error_contract() -> None:
    with pytest.raises(CommandCenterDataError, match="could not be prepared"):
        MockCommandCenterService().snapshot("malformed")


def test_command_center_renders_fixture_data_and_inspect_actions() -> None:
    app = AppTest.from_file(COMMAND_CENTER_PATH, default_timeout=10).run()
    assert not app.exception
    page_text = " ".join(item.value for item in app.markdown)
    assert "Operational demo metrics" in page_text
    assert "CUST-HIGH-001" in page_text
    assert "CUST-HARD-001" in page_text
    assert "Model evaluation pending" in page_text
    assert '/app/predict?fixture=CUST-HIGH-001' in page_text


def test_command_center_empty_and_error_states_render() -> None:
    empty = AppTest.from_file(COMMAND_CENTER_PATH, default_timeout=10).run()
    empty.selectbox[0].select("Empty demo history").run()
    assert "No analyzed customers yet" in " ".join(
        item.value for item in empty.markdown
    )

    malformed = AppTest.from_file(COMMAND_CENTER_PATH, default_timeout=10).run()
    malformed.selectbox[0].select("Malformed demo history").run()
    assert len(malformed.error) == 1
    assert "could not be loaded" in malformed.error[0].value
