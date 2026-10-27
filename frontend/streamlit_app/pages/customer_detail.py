from __future__ import annotations

import re
import sys
from html import escape
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from frontend.streamlit_app.models import (
    CustomerDetailResult,
    DriverDirection,
    RiskLabel,
)
from frontend.streamlit_app.services import (
    CustomerDetailDataError,
    CustomerDetailNotFound,
    MockCustomerDetailService,
)
from frontend.streamlit_app.services.customer_detail import CustomerDetailMode
from frontend.streamlit_app.ui.components import app_shell


RISK_PRESENTATION = {
    RiskLabel.LOW: (
        "low",
        "LOW RISK",
        "Stable demo signal",
    ),
    RiskLabel.MEDIUM: (
        "watch",
        "MEDIUM / REVIEW",
        "Near the operating threshold",
    ),
    RiskLabel.HIGH: (
        "high",
        "HIGH RISK",
        "Prioritize operator review",
    ),
}
SAFE_FIXTURE = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


@st.cache_resource
def get_customer_detail_service() -> MockCustomerDetailService:
    return MockCustomerDetailService()


def reset_detail_mode() -> None:
    st.session_state.customer_detail_mode = "Customer fixture"


def detail_actions(customer_id: str | None = None) -> None:
    prediction = (
        f'<a href="/app/predict?fixture={escape(customer_id)}" '
        f'aria-label="Open {escape(customer_id)} in Prediction Workspace">'
        "Open Prediction Workspace →</a>"
        if customer_id
        else ""
    )
    explanation = (
        f'<a href="/app/model-explanations?fixture={escape(customer_id)}" '
        f'aria-label="Open demo explanation for {escape(customer_id)}">'
        "Why this prediction? →</a>"
        if customer_id
        else ""
    )
    st.markdown(
        '<nav class="cd-actions" aria-label="Customer Detail actions">'
        '<a href="/app/customers">← Back to Customer History</a>'
        f"{prediction}"
        f"{explanation}"
        '<a href="/app">Command Center</a>'
        "</nav>",
        unsafe_allow_html=True,
    )


def render_missing() -> None:
    st.markdown(
        '<div class="cg-mobile-brand">ChurnGuard · Customer Detail</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="cg-kicker">Customer record / deterministic demo</p>',
        unsafe_allow_html=True,
    )
    st.title("Select a customer")
    st.markdown(
        '<p class="cg-subhead">Customer Detail needs an approved fixture identifier '
        "from Customer History.</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="cd-state"><strong>No customer selected</strong>'
        "<p>Return to Customer History and choose a deterministic customer record.</p>"
        '<a href="/app/customers">Browse Customer History →</a></div>',
        unsafe_allow_html=True,
    )
    detail_actions()


def render_not_found(customer_id: str | None, *, malformed: bool = False) -> None:
    st.markdown(
        '<div class="cg-mobile-brand">ChurnGuard · Customer Detail</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="cg-kicker">Customer record / deterministic demo</p>',
        unsafe_allow_html=True,
    )
    st.title("Customer not found")
    detail = (
        "The supplied customer identifier is malformed and was not processed."
        if malformed
        else f"{escape(customer_id or '')} is not available in the approved demo set."
    )
    st.markdown(
        f'<div class="cd-state"><strong>Unable to open this customer</strong>'
        f"<p>{detail}</p>"
        '<a href="/app/customers">Return to Customer History →</a></div>',
        unsafe_allow_html=True,
    )
    detail_actions()


def render_header(detail: CustomerDetailResult) -> None:
    customer = detail.customer
    prediction = detail.prediction
    _, badge, _ = RISK_PRESENTATION[prediction.risk_label]
    st.markdown(
        '<div class="cg-mobile-brand">ChurnGuard · Customer Detail</div>',
        unsafe_allow_html=True,
    )
    detail_actions(customer.customer_id)
    st.markdown(
        '<p class="cg-kicker">Customer record / deterministic demo</p>',
        unsafe_allow_html=True,
    )
    st.title(customer.customer_id)
    st.markdown(
        f'<p class="cg-subhead">{escape(customer.contract)} contract · '
        f"{customer.tenure} months tenure · {escape(customer.internet_service)} internet. "
        "Inspect the current fixture signal, its reasons, and the recommended operator response.</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
<div class="cd-identity" aria-label="Customer operating context">
  <div><span>Current status</span><strong>{escape(badge)}</strong></div>
  <div><span>Predicted churn risk</span><strong>{prediction.risk_probability * 100:.0f}%</strong></div>
  <div><span>Prediction time</span><strong>{prediction.generated_at.strftime("%d %b %Y · %H:%M UTC")}</strong></div>
  <div><span>Data status</span><strong>Approved demo fixture</strong></div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_risk_brief(detail: CustomerDetailResult) -> None:
    prediction = detail.prediction
    risk_class, badge, interpretation = RISK_PRESENTATION[prediction.risk_label]
    probability = round(prediction.risk_probability * 100)
    threshold = round(prediction.threshold * 100)
    scenario = (
        "Conflicting retention and risk signals make this a review-worthy hard case."
        if prediction.scenario == "hard_case"
        else prediction.scenario_description
    )
    st.subheader("Risk brief")
    st.markdown(
        f"""
<section class="cd-risk {risk_class}" aria-label="Current churn risk">
  <div class="cd-risk-top">
    <div><span>Predicted churn risk</span><strong>{probability}%</strong></div>
    <b>● {escape(badge)}</b>
  </div>
  <div class="cd-meter" aria-label="Risk probability {probability} percent; operating threshold {threshold} percent">
    <div style="width:{probability}%"></div><i style="left:{threshold}%"></i>
  </div>
  <div class="cd-meter-labels"><span>0% lower signal</span><span>{threshold}% threshold</span><span>100% higher signal</span></div>
  <p><strong>{escape(interpretation)}.</strong> {escape(scenario)}</p>
</section>
""",
        unsafe_allow_html=True,
    )


def render_explanation(detail: CustomerDetailResult) -> None:
    prediction = detail.prediction
    explanation = (
        "High charges and electronic-check billing raise the demo signal, while the "
        "one-year contract provides a conflicting retention signal. Human review is appropriate."
        if prediction.scenario == "hard_case"
        else prediction.scenario_description
    )
    st.subheader("Plain-English explanation")
    st.markdown(
        f'<div class="cd-explanation"><strong>Why this customer is here</strong>'
        f"<p>{escape(explanation)}</p>"
        "<small>This interpretation restates deterministic fixture evidence. It is not a causal or real-model explanation.</small></div>",
        unsafe_allow_html=True,
    )


def render_drivers(detail: CustomerDetailResult) -> None:
    st.subheader("Top drivers")
    st.caption(
        "Three deterministic fixture contributions—not real SHAP values or causal evidence."
    )
    rows = []
    for index, (driver, supporting_value) in enumerate(
        zip(detail.prediction.top_drivers, detail.driver_values, strict=True),
        start=1,
    ):
        raises = driver.direction == DriverDirection.INCREASES
        direction = "Raises risk" if raises else "Lowers risk"
        symbol = "↑" if raises else "↓"
        value = (
            f"<span>Customer value</span><strong>{escape(supporting_value)}</strong>"
            if supporting_value
            else ""
        )
        rows.append(
            f"""
<li class="cd-driver {'raises' if raises else 'lowers'}">
  <div class="cd-driver-rank">{index:02d}</div>
  <div class="cd-driver-main">
    <strong>{escape(driver.feature)}</strong>
    <p>{escape(driver.explanation)}</p>
  </div>
  <div class="cd-driver-signal"><span>{symbol} {direction}</span><strong>{driver.impact:+.2f}</strong></div>
  <div class="cd-driver-value">{value}</div>
</li>
"""
        )
    st.markdown(
        '<ol class="cd-drivers" aria-label="Ranked customer risk drivers">'
        + "".join(rows)
        + "</ol>",
        unsafe_allow_html=True,
    )


def render_recommendation(detail: CustomerDetailResult) -> None:
    recommendation = detail.prediction.recommendation
    actions = "".join(f"<li>{escape(action)}</li>" for action in recommendation.actions)
    st.subheader("Retention recommendation")
    st.markdown(
        f'<section class="cd-recommendation"><span>Decision support · {escape(recommendation.priority.value)} priority</span>'
        f"<strong>{escape(recommendation.summary)}</strong><ul>{actions}</ul>"
        "<small>Use operator judgment. This demo recommendation is not a claim of proven churn reduction.</small></section>",
        unsafe_allow_html=True,
    )


def render_context(detail: CustomerDetailResult) -> None:
    customer = detail.customer
    st.subheader("Customer and account context")
    st.caption("Fixture attributes grouped for inspection; no profile data is inferred.")
    senior = "Yes" if customer.senior_citizen else "No"
    st.markdown(
        f"""
<div class="cd-context">
  <section aria-labelledby="customer-context-heading">
    <h3 id="customer-context-heading">Customer</h3>
    <dl>
      <div><dt>Gender</dt><dd>{escape(customer.gender)}</dd></div>
      <div><dt>Senior citizen</dt><dd>{senior}</dd></div>
      <div><dt>Partner</dt><dd>{escape(customer.partner)}</dd></div>
      <div><dt>Dependents</dt><dd>{escape(customer.dependents)}</dd></div>
    </dl>
  </section>
  <section aria-labelledby="account-context-heading">
    <h3 id="account-context-heading">Account</h3>
    <dl>
      <div><dt>Tenure</dt><dd>{customer.tenure} months</dd></div>
      <div><dt>Contract</dt><dd>{escape(customer.contract)}</dd></div>
      <div><dt>Payment</dt><dd>{escape(customer.payment_method)}</dd></div>
      <div><dt>Paperless billing</dt><dd>{escape(customer.paperless_billing)}</dd></div>
      <div><dt>Monthly charges</dt><dd>${customer.monthly_charges:,.2f}</dd></div>
      <div><dt>Total charges</dt><dd>${customer.total_charges:,.2f}</dd></div>
    </dl>
  </section>
  <section aria-labelledby="services-context-heading">
    <h3 id="services-context-heading">Services</h3>
    <dl>
      <div><dt>Internet</dt><dd>{escape(customer.internet_service)}</dd></div>
      <div><dt>Phone</dt><dd>{escape(customer.phone_service)}</dd></div>
      <div><dt>Multiple lines</dt><dd>{escape(customer.multiple_lines)}</dd></div>
      <div><dt>Online security</dt><dd>{escape(customer.online_security)}</dd></div>
      <div><dt>Online backup</dt><dd>{escape(customer.online_backup)}</dd></div>
      <div><dt>Device protection</dt><dd>{escape(customer.device_protection)}</dd></div>
      <div><dt>Tech support</dt><dd>{escape(customer.tech_support)}</dd></div>
      <div><dt>Streaming TV</dt><dd>{escape(customer.streaming_tv)}</dd></div>
      <div><dt>Streaming movies</dt><dd>{escape(customer.streaming_movies)}</dd></div>
    </dl>
  </section>
</div>
""",
        unsafe_allow_html=True,
    )


def render_prediction_context(detail: CustomerDetailResult) -> None:
    prediction = detail.prediction
    st.subheader("Prediction context")
    st.markdown(
        f"""
<dl class="cd-prediction-context">
  <div><dt>Prediction ID</dt><dd>{escape(prediction.prediction_id)}</dd></div>
  <div><dt>Timestamp</dt><dd>{prediction.generated_at.strftime("%d %b %Y · %H:%M UTC")}</dd></div>
  <div><dt>Operating threshold</dt><dd>{prediction.threshold * 100:.0f}%</dd></div>
  <div><dt>Model version</dt><dd>{escape(prediction.model_version)}</dd></div>
  <div><dt>Source</dt><dd>Deterministic JSON fixture</dd></div>
  <div><dt>Service</dt><dd>{escape(detail.service_status)}</dd></div>
</dl>
""",
        unsafe_allow_html=True,
    )


app_shell("Customer Detail")
service = get_customer_detail_service()

with st.sidebar.expander("Demo state controls", expanded=False):
    selected_mode = st.selectbox(
        "Customer Detail data state",
        ["Customer fixture", "Malformed demo record"],
        key="customer_detail_mode",
        help="Development-only control for proving the recoverable data-error state.",
    )

raw_fixture = st.query_params.get("fixture")
pending_fixture = st.session_state.pop("detail_route_fixture", None)
fixture_id = raw_fixture if isinstance(raw_fixture, str) else pending_fixture
if (
    not isinstance(raw_fixture, str)
    and isinstance(pending_fixture, str)
    and pending_fixture
):
    st.query_params["fixture"] = pending_fixture

if fixture_id is None or not fixture_id.strip():
    render_missing()
elif not SAFE_FIXTURE.fullmatch(fixture_id):
    render_not_found(None, malformed=True)
else:
    mode: CustomerDetailMode = (
        "malformed" if selected_mode == "Malformed demo record" else "sample"
    )
    try:
        with st.spinner("Loading deterministic customer record…"):
            detail = service.detail(fixture_id, mode=mode)
    except CustomerDetailNotFound:
        render_not_found(fixture_id)
    except CustomerDetailDataError:
        st.markdown(
            '<div class="cg-mobile-brand">ChurnGuard · Customer Detail</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<p class="cg-kicker">Customer record / deterministic demo</p>',
            unsafe_allow_html=True,
        )
        st.title("Customer record unavailable")
        st.error(
            "The demo customer record could not be loaded. No customer data was changed.",
            icon="⚠️",
        )
        st.caption("Return to the approved fixture record and retry.")
        st.button("Retry customer fixture", on_click=reset_detail_mode)
        detail_actions(fixture_id)
    else:
        render_header(detail)
        primary, secondary = st.columns([1.05, 0.95], gap="large")
        with primary:
            render_risk_brief(detail)
        with secondary:
            render_explanation(detail)
        render_drivers(detail)
        render_recommendation(detail)
        render_context(detail)
        render_prediction_context(detail)