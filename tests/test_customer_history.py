from datetime import date

import pytest
from streamlit.testing.v1 import AppTest

from frontend.streamlit_app.models import RiskLabel
from frontend.streamlit_app.services import (
    CustomerHistoryDataError,
    CustomerHistoryQuery,
    MockCustomerHistoryService,
)


CUSTOMER_HISTORY_PATH = "frontend/streamlit_app/pages/customers.py"
PREDICT_PATH = "frontend/streamlit_app/pages/predict.py"


def customer_ids(query: CustomerHistoryQuery) -> list[str]:
    result = MockCustomerHistoryService().query(query)
    return [row.customer_id for row in result.rows]


def test_customer_history_loads_all_deterministic_records() -> None:
    result = MockCustomerHistoryService().query()
    assert result.total_count == 4
    assert result.filtered_count == 4
    assert {row.customer_id for row in result.rows} == {
        "CUST-LOW-001",
        "CUST-HIGH-001",
        "CUST-BORDERLINE-001",
        "CUST-HARD-001",
    }
    assert result.is_demo_data is True


def test_customer_history_search_and_no_match() -> None:
    assert customer_ids(CustomerHistoryQuery(search="borderline")) == [
        "CUST-BORDERLINE-001"
    ]
    assert customer_ids(CustomerHistoryQuery(search="not-a-customer")) == []


def test_customer_history_risk_filter() -> None:
    assert customer_ids(CustomerHistoryQuery(risk=RiskLabel.HIGH)) == [
        "CUST-HIGH-001",
        "CUST-HARD-001",
    ]
    assert customer_ids(CustomerHistoryQuery(risk=RiskLabel.MEDIUM)) == [
        "CUST-BORDERLINE-001"
    ]


def test_customer_history_contract_filter_uses_fixture_values() -> None:
    assert customer_ids(CustomerHistoryQuery(contract="Month-to-month")) == [
        "CUST-HIGH-001",
        "CUST-BORDERLINE-001",
    ]
    result = MockCustomerHistoryService().query()
    assert result.available_contracts == ["Month-to-month", "One year", "Two year"]


@pytest.mark.parametrize(
    ("bucket", "expected"),
    [
        ("0-12", ["CUST-HIGH-001"]),
        ("13-36", ["CUST-HARD-001", "CUST-BORDERLINE-001"]),
        ("37+", ["CUST-LOW-001"]),
    ],
)
def test_customer_history_tenure_buckets(
    bucket: str,
    expected: list[str],
) -> None:
    assert customer_ids(CustomerHistoryQuery(tenure_bucket=bucket)) == expected  # type: ignore[arg-type]


def test_customer_history_date_filter_uses_fixture_timestamp() -> None:
    fixture_date = date(2026, 10, 4)
    result = MockCustomerHistoryService().query(
        CustomerHistoryQuery(prediction_date=fixture_date)
    )
    assert result.filtered_count == 4
    assert result.available_dates == [fixture_date]
    assert customer_ids(CustomerHistoryQuery(prediction_date=date(2026, 10, 5))) == []


def test_customer_history_sorting_is_deterministic() -> None:
    assert customer_ids(CustomerHistoryQuery(sort="risk_desc")) == [
        "CUST-HIGH-001",
        "CUST-HARD-001",
        "CUST-BORDERLINE-001",
        "CUST-LOW-001",
    ]
    assert customer_ids(CustomerHistoryQuery(sort="risk_asc")) == [
        "CUST-LOW-001",
        "CUST-BORDERLINE-001",
        "CUST-HARD-001",
        "CUST-HIGH-001",
    ]
    assert customer_ids(CustomerHistoryQuery(sort="newest")) == [
        "CUST-BORDERLINE-001",
        "CUST-HARD-001",
        "CUST-HIGH-001",
        "CUST-LOW-001",
    ]


def test_customer_history_combined_filters() -> None:
    assert customer_ids(
        CustomerHistoryQuery(
            search="month-to-month",
            risk=RiskLabel.HIGH,
            contract="Month-to-month",
            tenure_bucket="0-12",
            prediction_date=date(2026, 10, 4),
        )
    ) == ["CUST-HIGH-001"]


def test_customer_history_empty_and_error_contracts() -> None:
    empty = MockCustomerHistoryService().query(mode="empty")
    assert empty.rows == []
    assert empty.total_count == 0
    assert empty.filtered_count == 0
    with pytest.raises(CustomerHistoryDataError, match="could not be prepared"):
        MockCustomerHistoryService().query(mode="malformed")


def test_customer_history_page_renders_table_and_inspect_actions() -> None:
    app = AppTest.from_file(CUSTOMER_HISTORY_PATH, default_timeout=10).run()
    assert not app.exception
    page_text = " ".join(item.value for item in app.markdown)
    for customer_id in (
        "CUST-LOW-001",
        "CUST-HIGH-001",
        "CUST-BORDERLINE-001",
        "CUST-HARD-001",
    ):
        assert customer_id in page_text
        assert f"/app/customer-detail?fixture={customer_id}" in page_text
    assert "<table" in page_text


def test_customer_history_page_search_and_no_results() -> None:
    app = AppTest.from_file(CUSTOMER_HISTORY_PATH, default_timeout=10).run()
    app.text_input(key="history_search").set_value("CUST-LOW-001").run()
    page_text = " ".join(item.value for item in app.markdown)
    assert "1</strong> of 4" in page_text
    assert "CUST-LOW-001" in page_text

    app.text_input(key="history_search").set_value("NO-SUCH-CUSTOMER").run()
    assert "No customers match this search" in " ".join(
        item.value for item in app.markdown
    )


def test_customer_history_page_filter_no_results_and_reset() -> None:
    app = AppTest.from_file(CUSTOMER_HISTORY_PATH, default_timeout=10).run()
    app.selectbox(key="history_risk").select("Low").run()
    app.selectbox(key="history_contract").select("Month-to-month").run()
    assert "No customers match these filters" in " ".join(
        item.value for item in app.markdown
    )
    app.button[2].click().run()
    assert "4</strong> of 4" in " ".join(item.value for item in app.markdown)


def test_customer_history_page_empty_and_error_states() -> None:
    empty = AppTest.from_file(CUSTOMER_HISTORY_PATH, default_timeout=10).run()
    empty.selectbox(key="customer_history_mode").select("Empty demo history").run()
    assert "No customer history exists" in " ".join(
        item.value for item in empty.markdown
    )

    malformed = AppTest.from_file(CUSTOMER_HISTORY_PATH, default_timeout=10).run()
    malformed.selectbox(key="customer_history_mode").select(
        "Malformed demo history"
    ).run()
    assert "could not be loaded" in malformed.error[0].value


def test_selected_customer_reaches_existing_prediction_workflow() -> None:
    app = AppTest.from_file(PREDICT_PATH, default_timeout=10)
    app.query_params["fixture"] = "CUST-HIGH-001"
    app.run()
    assert not app.exception
    assert app.text_input(key="field_customerID").value == "CUST-HIGH-001"
    assert app.selectbox(key="selected_fixture").value == "CUST-HIGH-001"