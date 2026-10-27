from __future__ import annotations

import sys
from datetime import date
from html import escape
from pathlib import Path
from typing import cast

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from frontend.streamlit_app.models import (
    Contract,
    CustomerHistoryResult,
    PredictionHistoryRow,
    RiskLabel,
)
from frontend.streamlit_app.services import (
    CustomerHistoryDataError,
    CustomerHistoryQuery,
    MockCustomerHistoryService,
)
from frontend.streamlit_app.services.customer_history import (
    CustomerHistoryMode,
    HistorySort,
    TenureBucket,
)
from frontend.streamlit_app.ui.components import app_shell


RISK_CLASS = {
    RiskLabel.LOW: "low",
    RiskLabel.MEDIUM: "watch",
    RiskLabel.HIGH: "high",
}
RISK_LABEL = {
    RiskLabel.LOW: "Low",
    RiskLabel.MEDIUM: "Medium / Watch",
    RiskLabel.HIGH: "High",
}
RISK_OPTIONS = {
    "All risk bands": None,
    "Low": RiskLabel.LOW,
    "Watch / Medium": RiskLabel.MEDIUM,
    "High": RiskLabel.HIGH,
}
TENURE_OPTIONS = {
    "All tenure": "all",
    "0–12 months": "0-12",
    "13–36 months": "13-36",
    "37+ months": "37+",
}
SORT_OPTIONS = {
    "Highest risk first": "risk_desc",
    "Lowest risk first": "risk_asc",
    "Newest prediction": "newest",
    "Oldest prediction": "oldest",
}


@st.cache_resource
def get_customer_history_service() -> MockCustomerHistoryService:
    return MockCustomerHistoryService()


def reset_history_controls() -> None:
    st.session_state.history_search = ""
    st.session_state.history_risk = "All risk bands"
    st.session_state.history_contract = "All contracts"
    st.session_state.history_tenure = "All tenure"
    st.session_state.history_date = "All fixture dates"
    st.session_state.history_sort = "Highest risk first"


def clear_history_search() -> None:
    st.session_state.history_search = ""


def reset_history_mode() -> None:
    st.session_state.customer_history_mode = "Sample demo history"


def render_header(result: CustomerHistoryResult | None, *, failed: bool = False) -> None:
    status = (
        "Demo history unavailable"
        if failed
        else result.service_status if result else "Demo fixture service"
    )
    version = result.model_version if result else "demo-fixture-v1.0.0"
    snapshot = (
        result.generated_at.strftime("%d %b %Y · %H:%M UTC")
        if result
        else "Fixed frontend demo context"
    )
    st.markdown(
        '<div class="cg-mobile-brand">ChurnGuard · Customer History</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="cg-kicker">Operations / deterministic prediction history</p>',
        unsafe_allow_html=True,
    )
    st.title("Customer History")
    st.markdown(
        '<p class="cg-subhead">Search and prioritize previously analyzed sample '
        "customers, then open the accepted customer-analysis workflow for inspection.</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="cg-demo"><strong>Demo history.</strong> Every customer, probability, '
        "driver, timestamp, and model version comes from the approved deterministic "
        "frontend fixtures. No production activity is represented.</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
<div class="cc-statusline" aria-label="Customer History context">
  <div><span>Model state</span><strong>{escape(version)} · demo only</strong></div>
  <div><span>Service</span><strong>{escape(status)}</strong></div>
  <div><span>Fixture snapshot</span><strong>{escape(snapshot)}</strong></div>
</div>
""",
        unsafe_allow_html=True,
    )


def row_markup(row: PredictionHistoryRow) -> tuple[str, str]:
    risk_class = RISK_CLASS[row.risk_label]
    risk_label = RISK_LABEL[row.risk_label]
    probability = f"{row.risk_probability * 100:.0f}%"
    predicted_at = row.predicted_at.strftime("%d %b %Y · %H:%M UTC")
    inspect_url = f"/app/customer-detail?fixture={escape(row.customer_id)}"
    desktop = f"""
<tr>
  <th scope="row">{escape(row.customer_id)}</th>
  <td class="ch-probability">{probability}</td>
  <td><span class="cc-risk {risk_class}">● {escape(risk_label)}</span></td>
  <td>{escape(row.top_driver)}</td>
  <td>{row.tenure} mo</td>
  <td>{escape(row.contract)}</td>
  <td><time>{escape(predicted_at)}</time></td>
  <td>{escape(row.model_version)}</td>
  <td><a class="cc-inspect" href="{inspect_url}" aria-label="Inspect {escape(row.customer_id)}">Inspect →</a></td>
</tr>
"""
    mobile = f"""
<li class="ch-card">
  <div class="ch-card-head">
    <div><span>Customer</span><strong>{escape(row.customer_id)}</strong></div>
    <span class="cc-risk {risk_class}">● {escape(risk_label)}</span>
  </div>
  <div class="ch-card-signal">
    <div><span>Predicted churn risk</span><strong>{probability}</strong></div>
    <div><span>Top driver</span><strong>{escape(row.top_driver)}</strong></div>
  </div>
  <details>
    <summary>Supporting details</summary>
    <dl>
      <div><dt>Tenure</dt><dd>{row.tenure} months</dd></div>
      <div><dt>Contract</dt><dd>{escape(row.contract)}</dd></div>
      <div><dt>Prediction</dt><dd>{escape(predicted_at)}</dd></div>
      <div><dt>Model</dt><dd>{escape(row.model_version)}</dd></div>
    </dl>
  </details>
  <a class="cc-inspect" href="{inspect_url}" aria-label="Inspect {escape(row.customer_id)}">Inspect customer →</a>
</li>
"""
    return desktop, mobile


def render_history(result: CustomerHistoryResult) -> None:
    desktop_rows = []
    mobile_rows = []
    for row in result.rows:
        desktop, mobile = row_markup(row)
        desktop_rows.append(desktop)
        mobile_rows.append(mobile)

    st.markdown(
        f"""
<div class="ch-results-summary" role="status">
  <strong>{result.filtered_count}</strong> of {result.total_count} approved sample customers shown
</div>
<div class="ch-table-wrap">
  <table class="ch-table">
    <caption>Deterministic customer prediction history</caption>
    <thead><tr>
      <th scope="col">Customer ID</th><th scope="col">Probability</th>
      <th scope="col">Risk</th><th scope="col">Top driver</th>
      <th scope="col">Tenure</th><th scope="col">Contract</th>
      <th scope="col">Prediction timestamp</th><th scope="col">Model version</th>
      <th scope="col">Action</th>
    </tr></thead>
    <tbody>{''.join(desktop_rows)}</tbody>
  </table>
</div>
<ul class="ch-mobile-list" aria-label="Deterministic customer prediction history">
  {''.join(mobile_rows)}
</ul>
""",
        unsafe_allow_html=True,
    )


def render_no_results(*, has_search: bool) -> None:
    if has_search:
        title = "No customers match this search"
        copy = "Clear the search or try a customer ID, contract, scenario, or top driver."
    else:
        title = "No customers match these filters"
        copy = "Reset the filters to return to the complete deterministic history."
    st.markdown(
        f'<div class="cc-empty"><strong>{title}</strong><p>{copy}</p></div>',
        unsafe_allow_html=True,
    )
    st.button("Reset search and filters", on_click=reset_history_controls)


app_shell("Customer History")
service = get_customer_history_service()

with st.sidebar.expander("Demo state controls", expanded=False):
    selected_mode = st.selectbox(
        "Customer History data state",
        ["Sample demo history", "Empty demo history", "Malformed demo history"],
        key="customer_history_mode",
        help="Development-only controls for proving supported history states.",
    )

mode_map: dict[str, CustomerHistoryMode] = {
    "Sample demo history": "sample",
    "Empty demo history": "empty",
    "Malformed demo history": "malformed",
}

try:
    baseline = service.query(mode=mode_map[selected_mode])
except CustomerHistoryDataError:
    render_header(None, failed=True)
    st.error(
        "The demo customer history could not be loaded. No customer data was changed.",
        icon="⚠️",
    )
    st.caption("Return to the approved sample history and retry.")
    st.button("Retry sample history", on_click=reset_history_mode)
else:
    render_header(baseline)
    if baseline.total_count == 0:
        st.markdown(
            '<div class="cc-empty"><strong>No customer history exists</strong>'
            "<p>Run a sample prediction before using history to prioritize customers.</p>"
            '<a href="/app/predict">Analyze a sample customer →</a></div>',
            unsafe_allow_html=True,
        )
    else:
        st.subheader("Find analyzed customers")
        st.caption(
            "Search fixture fields and combine risk, contract, tenure, and fixture-date filters."
        )
        search_col, clear_col = st.columns([5, 1])
        with search_col:
            search = st.text_input(
                "Search customer history",
                key="history_search",
                placeholder="Customer ID, top driver, contract, or scenario",
            )
        with clear_col:
            st.markdown(
                '<div class="ch-clear-label">Search</div>', unsafe_allow_html=True
            )
            st.button(
                "Clear",
                key="clear_history_search",
                on_click=clear_history_search,
                disabled=not bool(search),
                use_container_width=True,
            )

        filter_a, filter_b, filter_c, filter_d = st.columns(4)
        with filter_a:
            risk_selection = st.selectbox(
                "Risk", list(RISK_OPTIONS), key="history_risk"
            )
        contract_options = ["All contracts", *baseline.available_contracts]
        with filter_b:
            contract_selection = st.selectbox(
                "Contract", contract_options, key="history_contract"
            )
        with filter_c:
            tenure_selection = st.selectbox(
                "Tenure", list(TENURE_OPTIONS), key="history_tenure"
            )
        date_labels: dict[str, date | None] = {
            "All fixture dates": None,
            **{item.strftime("%d %b %Y"): item for item in baseline.available_dates},
        }
        with filter_d:
            date_selection = st.selectbox(
                "Prediction date", list(date_labels), key="history_date"
            )

        sort_col, reset_col = st.columns([2, 1])
        with sort_col:
            sort_selection = st.selectbox(
                "Sort", list(SORT_OPTIONS), key="history_sort"
            )
        with reset_col:
            st.markdown(
                '<div class="ch-clear-label">Filters</div>', unsafe_allow_html=True
            )
            st.button(
                "Reset all",
                on_click=reset_history_controls,
                use_container_width=True,
            )

        query = CustomerHistoryQuery(
            search=search,
            risk=RISK_OPTIONS[risk_selection],
            contract=cast(
                Contract | None,
                None if contract_selection == "All contracts" else contract_selection,
            ),
            tenure_bucket=cast(TenureBucket, TENURE_OPTIONS[tenure_selection]),
            prediction_date=date_labels[date_selection],
            sort=cast(HistorySort, SORT_OPTIONS[sort_selection]),
        )
        result = service.query(query)
        st.subheader("Prediction history")
        st.caption(
            "One fixed fixture snapshot. Sorting uses deterministic values and customer ID tie-breaks."
        )
        if result.rows:
            render_history(result)
        else:
            render_no_results(has_search=bool(search.strip()))