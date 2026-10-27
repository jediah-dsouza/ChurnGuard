from __future__ import annotations

import sys
from html import escape
from pathlib import Path
from typing import cast

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from frontend.streamlit_app.models import (
    DriverDirection,
    GlobalExplanationResult,
    LocalExplanationResult,
    RiskLabel,
)
from frontend.streamlit_app.services import (
    ExplanationDataError,
    ExplanationNotFound,
    ExplanationServiceError,
    MockExplanationService,
)
from frontend.streamlit_app.services.explanations import (
    GlobalExplanationMode,
    LocalExplanationMode,
)
from frontend.streamlit_app.ui.components import app_shell


GLOBAL_MODES: dict[str, GlobalExplanationMode] = {
    "Populated demo view": "sample",
    "Empty demo view": "empty",
    "Explanation unavailable": "unavailable",
    "Malformed global data": "malformed",
    "Global service error": "error",
}
LOCAL_MODES: dict[str, LocalExplanationMode] = {
    "Available demo explanation": "sample",
    "Explanation unavailable": "unavailable",
    "Malformed explanation": "malformed",
    "Local service error": "error",
}
RISK_CLASS = {
    RiskLabel.LOW: "low",
    RiskLabel.MEDIUM: "watch",
    RiskLabel.HIGH: "high",
}
RISK_LABEL = {
    RiskLabel.LOW: "Low",
    RiskLabel.MEDIUM: "Medium / Review",
    RiskLabel.HIGH: "High",
}


@st.cache_resource
def get_explanation_service() -> MockExplanationService:
    return MockExplanationService()


def initialize_state() -> None:
    st.session_state.setdefault("local_explanation_result", None)
    st.session_state.setdefault("local_explanation_error", None)
    st.session_state.setdefault("last_explanation_customer", None)


def clear_local_result() -> None:
    st.session_state.local_explanation_result = None
    st.session_state.local_explanation_error = None


def reset_global_mode() -> None:
    st.session_state.global_explanation_mode = "Populated demo view"


def load_local(
    service: MockExplanationService,
    customer_id: str,
    mode: LocalExplanationMode,
) -> None:
    st.session_state.last_explanation_customer = customer_id
    try:
        result = service.local_explanation(customer_id, mode=mode)
    except ExplanationNotFound:
        st.session_state.local_explanation_result = None
        st.session_state.local_explanation_error = (
            "not_found",
            "This customer is not available in the approved explanation fixtures.",
        )
    except ExplanationDataError:
        st.session_state.local_explanation_result = None
        st.session_state.local_explanation_error = (
            "malformed",
            "The demo explanation data could not be interpreted.",
        )
    except ExplanationServiceError:
        st.session_state.local_explanation_result = None
        st.session_state.local_explanation_error = (
            "service",
            "Explanation data could not be loaded. Retry to inspect this customer’s model drivers.",
        )
    else:
        st.session_state.local_explanation_result = result
        st.session_state.local_explanation_error = None


def retry_local(service: MockExplanationService) -> None:
    customer_id = st.session_state.last_explanation_customer
    if isinstance(customer_id, str):
        load_local(service, customer_id, "sample")


def render_header() -> None:
    st.markdown(
        '<div class="cg-mobile-brand">ChurnGuard · Model Explanations</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="cg-kicker">Model intelligence / deterministic explanation preview</p>',
        unsafe_allow_html=True,
    )
    st.title("Model Explanations")
    st.markdown(
        '<p class="cg-subhead">Inspect which supplied signals raise, lower, or '
        "complicate churn concern before deciding how to respond.</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="cg-demo"><strong>Demo explanation data.</strong> The views below '
        "use approved UI fixtures. They are not trained SHAP output, statistically "
        "validated global importance, or production model explanations.</div>",
        unsafe_allow_html=True,
    )


def render_global(result: GlobalExplanationResult) -> None:
    st.subheader("Global explanation preview")
    st.caption(
        "What signals are most influential across the current four demo examples?"
    )
    if result.status == "empty":
        st.markdown(
            '<div class="ex-state"><strong>No global explanation rows</strong>'
            "<p>The approved explanation dataset is empty. Load the populated demo "
            "view to inspect the supplied driver patterns.</p></div>",
            unsafe_allow_html=True,
        )
        return
    if result.status == "unavailable":
        st.markdown(
            '<div class="ex-state"><strong>Global explanation unavailable</strong>'
            "<p>No global driver summary is available. No substitute importance "
            "values or placeholder chart is shown.</p></div>",
            unsafe_allow_html=True,
        )
        return

    plot_rows = []
    table_rows = []
    for driver in result.drivers:
        direction = {
            "higher": "Higher-risk signal",
            "lower": "Lower-risk signal",
            "mixed": "Mixed direction",
        }[driver.direction]
        plot_rows.append(
            f"""
<li class="ex-global-driver">
  <div class="ex-global-label">
    <b>{driver.rank:02d}</b>
    <div><strong>{escape(driver.family)}</strong><span>{escape(direction)} · observed in {driver.observed_count} fixture{'s' if driver.observed_count != 1 else ''}</span></div>
    <em>{escape(driver.relative_influence)}</em>
  </div>
  <div class="ex-global-track" aria-label="Rank {driver.rank}; {escape(driver.family)}; {escape(driver.relative_influence)} relative influence">
    <div style="width:{driver.bar_percent:.1f}%"></div>
  </div>
</li>
"""
        )
        table_rows.append(
            f"""
<tr>
  <td>{driver.rank}</td>
  <th scope="row">{escape(driver.family)}</th>
  <td>{escape(direction)}</td>
  <td>{escape(driver.relative_influence)}</td>
  <td>{driver.observed_count} of {result.sample_size}</td>
  <td>{escape(driver.meaning)}</td>
</tr>
"""
        )
    st.markdown(
        f"""
<section class="ex-global" aria-label="Illustrative global driver summary">
  <div class="ex-honesty"><strong>Demo explanation view</strong><span>Based on {result.sample_size} approved sample fixtures—not a population estimate.</span></div>
  <ol class="ex-global-list">{''.join(plot_rows)}</ol>
</section>
<div class="ex-global-table">
  <table>
    <caption>Deterministic global explanation driver table</caption>
    <thead><tr>
      <th scope="col">Rank</th><th scope="col">Driver family</th>
      <th scope="col">Direction</th><th scope="col">Relative influence</th>
      <th scope="col">Observed</th><th scope="col">Plain-English meaning</th>
    </tr></thead>
    <tbody>{''.join(table_rows)}</tbody>
  </table>
</div>
<details class="ex-method">
  <summary>Methodology and limitations</summary>
  <p>{escape(result.methodology_note)}</p>
  <p>Driver families group the exact top-three fixture labels. Ranking uses the supplied absolute UI-fixture contributions only; direction remains mixed when approved fixtures disagree.</p>
</details>
""",
        unsafe_allow_html=True,
    )


def render_global_error(kind: str) -> None:
    if kind == "malformed":
        message = (
            "The demo global explanation data could not be interpreted. "
            "No driver ranking is shown."
        )
    else:
        message = (
            "Global explanation data could not be loaded. "
            "Retry to inspect the approved demo driver summary."
        )
    st.subheader("Global explanation preview")
    st.error(message, icon="⚠️")
    st.button("Retry global explanation", on_click=reset_global_mode)


def driver_markup(result: LocalExplanationResult) -> str:
    rows = []
    for driver in result.drivers:
        raises = driver.direction == DriverDirection.INCREASES
        direction = "Higher-risk signal" if raises else "Lower-risk signal"
        symbol = "↑" if raises else "↓"
        value = (
            f"<div><dt>Customer value</dt><dd>{escape(driver.supporting_value)}</dd></div>"
            if driver.supporting_value
            else ""
        )
        rows.append(
            f"""
<li class="ex-local-driver {'raises' if raises else 'lowers'}">
  <b>{driver.rank:02d}</b>
  <div class="ex-driver-copy">
    <strong>{escape(driver.feature)}</strong>
    <span>{symbol} {direction}</span>
    <p>{escape(driver.explanation)}</p>
    <details>
      <summary>Technical fixture context</summary>
      <dl>
        <div><dt>Driver family</dt><dd>{escape(driver.family)}</dd></div>
        <div><dt>Direction</dt><dd>{escape(direction)}</dd></div>
        <div><dt>Demo contribution</dt><dd>{driver.demo_contribution:+.2f}</dd></div>
        {value}
      </dl>
      <small>Illustrative fixture contribution—not SHAP, causality, or production evidence.</small>
    </details>
  </div>
</li>
"""
        )
    return "".join(rows)


def render_local(result: LocalExplanationResult) -> None:
    if result.status == "unavailable":
        st.markdown(
            f'<section class="ex-state" role="status"><strong>No explanation available for {escape(result.customer_id)}</strong>'
            f"<p>The {result.risk_probability * 100:.0f}% {escape(RISK_LABEL[result.risk_label])} demo risk remains available, "
            "but its explanation fixture is unavailable. No drivers are inferred.</p></section>",
            unsafe_allow_html=True,
        )
        return

    risk_class = RISK_CLASS[result.risk_label]
    risk_label = RISK_LABEL[result.risk_label]
    st.markdown(
        f"""
<section class="ex-local-head" aria-label="Customer explanation context">
  <div><span>Customer</span><strong>{escape(result.customer_id)}</strong></div>
  <div><span>Current demo risk</span><strong>{result.risk_probability * 100:.0f}% · {escape(risk_label)}</strong></div>
  <div><span>Explanation status</span><strong>{escape(result.explanation_status)}</strong></div>
  <div><span>Fixture version</span><strong>{escape(result.model_version)}</strong></div>
</section>
<section class="ex-risk {risk_class}" aria-label="{result.risk_probability * 100:.0f}% {escape(risk_label)} demo risk">
  <div><span>Predicted churn risk</span><strong>{result.risk_probability * 100:.0f}%</strong></div>
  <b>● {escape(risk_label)}</b>
  <p>{escape(result.plain_english_summary)}</p>
</section>
""",
        unsafe_allow_html=True,
    )
    if result.conflicting_signals:
        st.markdown(
            '<div class="ex-mixed" role="note"><strong>Mixed signals</strong>'
            "<span>The top fixture drivers include both higher- and lower-risk evidence. "
            "Use human review rather than treating the result as one-directional.</span></div>",
            unsafe_allow_html=True,
        )
    st.markdown("#### Why this result")
    st.caption(
        "Three ranked deterministic fixture drivers with direction stated in text."
    )
    st.markdown(
        f'<ol class="ex-local-drivers">{driver_markup(result)}</ol>',
        unsafe_allow_html=True,
    )

    if result.balancing_factors:
        balancing = "".join(
            f"<li><strong>{escape(driver.feature)}</strong><span>{escape(driver.explanation)}</span></li>"
            for driver in result.balancing_factors
        )
        st.markdown("#### Balancing signals")
        st.markdown(
            f'<ul class="ex-balancing">{balancing}</ul>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="ex-no-balance"><strong>No lower-risk signal in the top three</strong>'
            "<p>This describes only the supplied top-three fixture drivers; it does not prove that no other balancing evidence exists.</p></div>",
            unsafe_allow_html=True,
        )

    actions = "".join(f"<li>{escape(action)}</li>" for action in result.actions)
    st.markdown("#### Operator readout")
    st.markdown(
        f"""
<section class="ex-operator">
  <strong>{escape(result.operator_readout or 'No operator readout is available.')}</strong>
  <ul>{actions}</ul>
  <small>Decision support from a deterministic demo fixture—not evidence of proven retention impact.</small>
</section>
<nav class="ex-actions" aria-label="Explanation actions">
  <a href="/app/customer-detail?fixture={escape(result.customer_id)}">Return to Customer Detail</a>
  <a href="/app/predict?fixture={escape(result.customer_id)}">Open Prediction Workspace</a>
</nav>
""",
        unsafe_allow_html=True,
    )


def render_local_error(kind: str, customer_id: str | None) -> None:
    if kind == "not_found":
        title = "Customer explanation not found"
        detail = (
            f"{escape(customer_id or '')} is not available in the approved explanation fixtures."
        )
    elif kind == "malformed":
        title = "Explanation data cannot be interpreted"
        detail = "Return to the approved explanation fixture and retry."
    else:
        title = "Explanation service unavailable"
        detail = "Your selected customer is preserved for recovery."
    st.markdown(
        f'<section class="ex-state" role="alert"><strong>{title}</strong><p>{detail}</p></section>',
        unsafe_allow_html=True,
    )


app_shell("Model Explanations")
service = get_explanation_service()
initialize_state()
render_header()

with st.sidebar.expander("Demo state controls", expanded=False):
    global_mode_label = st.selectbox(
        "Global explanation state",
        list(GLOBAL_MODES),
        key="global_explanation_mode",
    )
    local_mode_label = st.selectbox(
        "Local explanation state",
        list(LOCAL_MODES),
        key="local_explanation_mode",
    )

try:
    global_result = service.global_explanation(
        mode=GLOBAL_MODES[global_mode_label]
    )
except ExplanationDataError:
    render_global_error("malformed")
except ExplanationServiceError:
    render_global_error("service")
else:
    render_global(global_result)

st.subheader("Local customer explanation")
st.caption(
    "Select an approved customer to connect current risk, ranked drivers, balancing evidence, and operator action."
)

fixture_ids = service.fixture_ids()
requested_fixture = st.query_params.get("fixture")
if (
    isinstance(requested_fixture, str)
    and requested_fixture in fixture_ids
    and st.session_state.get("explanation_route_fixture") != requested_fixture
):
    st.session_state.explanation_customer = requested_fixture
    st.session_state.explanation_route_fixture = requested_fixture
    load_local(service, requested_fixture, "sample")
elif (
    isinstance(requested_fixture, str)
    and requested_fixture not in fixture_ids
    and st.session_state.get("explanation_route_fixture") != requested_fixture
):
    st.session_state.explanation_route_fixture = requested_fixture
    load_local(service, requested_fixture, "sample")

selected_customer = st.selectbox(
    "Approved explanation customer",
    fixture_ids,
    index=None,
    placeholder="Choose a deterministic customer",
    key="explanation_customer",
    on_change=clear_local_result,
)
if st.button(
    "Load demo explanation",
    type="primary",
    disabled=selected_customer is None,
):
    with st.spinner("Loading deterministic explanation…"):
        load_local(
            service,
            cast(str, selected_customer),
            LOCAL_MODES[local_mode_label],
        )
    st.rerun()

local_error = st.session_state.local_explanation_error
local_result = st.session_state.local_explanation_result
if local_error:
    error_kind, _ = local_error
    customer_id = st.session_state.last_explanation_customer
    render_local_error(error_kind, customer_id)
    if error_kind in {"malformed", "service"}:
        if st.button("Retry customer explanation"):
            retry_local(service)
            st.rerun()
elif isinstance(local_result, LocalExplanationResult):
    render_local(local_result)
else:
    st.markdown(
        '<div class="ex-idle"><strong>No customer explanation selected</strong>'
        "<p>Choose an approved customer, then load the deterministic explanation preview.</p></div>",
        unsafe_allow_html=True,
    )