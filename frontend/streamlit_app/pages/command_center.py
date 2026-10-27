from __future__ import annotations

import sys
from html import escape
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from frontend.streamlit_app.models import CommandCenterSnapshot, RiskLabel
from frontend.streamlit_app.services import (
    CommandCenterDataError,
    MockCommandCenterService,
)
from frontend.streamlit_app.ui.components import app_shell


RISK_CLASS = {
    RiskLabel.LOW: "low",
    RiskLabel.MEDIUM: "watch",
    RiskLabel.HIGH: "high",
}


@st.cache_resource
def get_command_center_service() -> MockCommandCenterService:
    return MockCommandCenterService()


def percent(value: float | None) -> str:
    return "Demo data only" if value is None else f"{value * 100:.1f}%"


def timestamp(snapshot: CommandCenterSnapshot) -> str:
    return snapshot.generated_at.strftime("%d %b %Y · %H:%M UTC")


def render_header(snapshot: CommandCenterSnapshot | None, *, failed: bool = False) -> None:
    service_status = (
        "Demo snapshot unavailable"
        if failed
        else snapshot.service_status if snapshot else "Demo fixture service"
    )
    model_version = snapshot.model_version if snapshot else "demo-fixture-v1.0.0"
    context = timestamp(snapshot) if snapshot else "Fixed frontend demo context"
    st.markdown(
        '<div class="cg-mobile-brand">ChurnGuard · Command Center</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="cg-kicker">Operations / deterministic demo snapshot</p>',
        unsafe_allow_html=True,
    )
    st.title("Command Center")
    st.markdown(
        '<p class="cg-subhead">Triage the analyzed sample customers, find the signals '
        "that need review, and move directly into a customer risk brief.</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
<div class="cc-statusline" aria-label="Command Center context">
  <div><span>Model state</span><strong>{escape(model_version)} · demo only</strong></div>
  <div><span>Service</span><strong>{escape(service_status)}</strong></div>
  <div><span>Snapshot</span><strong>{escape(context)}</strong></div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_kpis(snapshot: CommandCenterSnapshot) -> None:
    kpis = snapshot.kpis
    st.markdown(
        f"""
<div class="cc-kpis" aria-label="Operational demo metrics">
  <div><span>Predictions analyzed</span><strong>{kpis.predictions_analyzed}</strong><small>approved fixtures</small></div>
  <div><span>High-risk customers</span><strong>{kpis.high_risk_customers}</strong><small>fixture label: High</small></div>
  <div><span>Average predicted risk</span><strong>{percent(kpis.average_predicted_risk)}</strong><small>demo snapshot mean</small></div>
  <div><span>Recent high-risk share</span><strong>{percent(kpis.recent_high_risk_share)}</strong><small>current fixture snapshot</small></div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_priority_queue(snapshot: CommandCenterSnapshot) -> None:
    st.subheader("Priority queue")
    st.caption(
        "Sorted by risk band, then probability. All rows are deterministic sample customers."
    )
    rows = []
    for row in snapshot.rows:
        risk_class = RISK_CLASS[row.risk_label]
        inspected_at = row.predicted_at.strftime("%d %b · %H:%M UTC")
        rows.append(
            f"""
<div class="cc-queue-row">
  <div class="cc-customer"><span>Customer</span><strong>{escape(row.customer_id)}</strong></div>
  <div><span>Risk</span><strong>{row.risk_probability * 100:.0f}%</strong></div>
  <div><span>Band</span><b class="cc-risk {risk_class}">● {escape(row.risk_label.value)}</b></div>
  <div class="cc-driver-cell"><span>Top driver</span><strong>{escape(row.top_driver)}</strong></div>
  <div><span>Tenure</span><strong>{row.tenure} mo</strong></div>
  <div><span>Contract</span><strong>{escape(row.contract)}</strong></div>
  <div><span>Fixture time</span><strong>{escape(inspected_at)}</strong></div>
  <div><a class="cc-inspect" href="/app/predict?fixture={escape(row.customer_id)}"
    aria-label="Inspect {escape(row.customer_id)}">Inspect →</a></div>
</div>
"""
        )
    st.markdown(
        '<div class="cc-queue" role="table" aria-label="Customer priority queue">'
        '<div class="cc-queue-head" aria-hidden="true">'
        "<span>Customer</span><span>Risk</span><span>Band</span><span>Top driver</span>"
        "<span>Tenure</span><span>Contract</span><span>Fixture time</span><span>Action</span>"
        "</div>"
        + "".join(rows)
        + "</div>",
        unsafe_allow_html=True,
    )


def render_distribution(snapshot: CommandCenterSnapshot) -> None:
    total = max(len(snapshot.rows), 1)
    distribution = [
        ("High", snapshot.distribution.high, "high"),
        ("Medium / Watch", snapshot.distribution.medium, "watch"),
        ("Low", snapshot.distribution.low, "low"),
    ]
    bars = "".join(
        f"""
<div class="cc-dist-row">
  <div><strong>{label}</strong><span>{count} of {len(snapshot.rows)}</span></div>
  <div class="cc-dist-track" aria-label="{label}: {count} of {len(snapshot.rows)}">
    <div class="cc-dist-fill {risk_class}" style="width:{count / total * 100:.1f}%"></div>
  </div>
</div>
"""
        for label, count, risk_class in distribution
    )
    threshold = (
        f"{snapshot.distribution.threshold * 100:.0f}%"
        if snapshot.distribution.threshold is not None
        else "not available"
    )
    st.subheader("Risk distribution")
    st.caption("Direct counts keep the four-customer demo snapshot interpretable.")
    st.markdown(
        f'<div class="cc-distribution">{bars}'
        f'<p>Operating threshold: <strong>{threshold}</strong> from the fixture contract.</p></div>',
        unsafe_allow_html=True,
    )


def render_review(snapshot: CommandCenterSnapshot) -> None:
    st.subheader("Needs review")
    st.caption("Customer predictions and supplied UI test states requiring attention.")
    items = []
    for item in snapshot.review_items:
        action = (
            f'<a href="/app/predict?fixture={escape(item.reference)}" '
            f'aria-label="Inspect {escape(item.reference)}">{escape(item.action)} →</a>'
            if item.category == "prediction"
            else f"<em>{escape(item.action)}</em>"
        )
        items.append(
            f"""
<div class="cc-review-item">
  <span>{escape(item.category)} · {escape(item.reference)}</span>
  <strong>{escape(item.title)}</strong>
  <p>{escape(item.detail)}</p>
  {action}
</div>
"""
        )
    st.markdown(
        '<div class="cc-review-list">' + "".join(items) + "</div>",
        unsafe_allow_html=True,
    )


def render_activity(snapshot: CommandCenterSnapshot) -> None:
    st.subheader("Recent prediction activity")
    st.caption(
        "Fixture order within one fixed demo snapshot; no production history is implied."
    )
    items = "".join(
        f"""
<div class="cc-activity-row">
  <div><strong>{escape(row.customer_id)}</strong><span>{escape(row.top_driver)}</span></div>
  <b class="cc-risk {RISK_CLASS[row.risk_label]}">● {escape(row.risk_label.value)}</b>
  <strong>{row.risk_probability * 100:.0f}%</strong>
  <time>{row.predicted_at.strftime("%H:%M UTC")}</time>
</div>
"""
        for row in snapshot.rows
    )
    st.markdown(
        '<div class="cc-activity-list">' + items + "</div>",
        unsafe_allow_html=True,
    )


def render_model_health(snapshot: CommandCenterSnapshot) -> None:
    st.subheader("Model health")
    st.caption("Intentional pre-ML state—no evaluation metrics are available yet.")
    st.markdown(
        f"""
<div class="cc-model-state">
  <strong>{escape(snapshot.evaluation_status)}</strong>
  <p>ROC-AUC, PR-AUC, recall, and calibration are pending real model artifacts.</p>
  <dl>
    <div><dt>Current source</dt><dd>Deterministic JSON fixtures</dd></div>
    <div><dt>Version</dt><dd>{escape(snapshot.model_version)}</dd></div>
    <div><dt>Inference</dt><dd>Mock service only</dd></div>
    <div><dt>Production API</dt><dd>Not connected</dd></div>
  </dl>
</div>
""",
        unsafe_allow_html=True,
    )


def reset_demo_mode() -> None:
    st.session_state.command_center_mode = "Sample demo snapshot"


app_shell("Command Center")
service = get_command_center_service()

with st.sidebar.expander("Demo state controls", expanded=False):
    selected_mode = st.selectbox(
        "Command Center data state",
        ["Sample demo snapshot", "Empty demo history", "Malformed demo history"],
        key="command_center_mode",
        help="Development-only controls for proving supported UI states.",
    )

mode_map = {
    "Sample demo snapshot": "sample",
    "Empty demo history": "empty",
    "Malformed demo history": "malformed",
}

try:
    snapshot = service.snapshot(mode_map[selected_mode])
except CommandCenterDataError:
    render_header(None, failed=True)
    st.error(
        "The demo activity snapshot could not be loaded. No customer data was changed.",
        icon="⚠️",
    )
    st.caption("Return to the approved sample snapshot and retry.")
    st.button("Retry sample snapshot", on_click=reset_demo_mode)
else:
    render_header(snapshot)
    render_kpis(snapshot)
    if not snapshot.rows:
        st.markdown(
            '<div class="cc-empty"><strong>No analyzed customers yet</strong>'
            "<p>Run your first prediction to begin building a retention queue.</p>"
            '<a href="/app/predict">Analyze a sample customer →</a></div>',
            unsafe_allow_html=True,
        )
    else:
        prediction_reviews = sum(
            item.category == "prediction" for item in snapshot.review_items
        )
        st.markdown(
            f'<div class="cc-attention"><strong>{snapshot.kpis.high_risk_customers} high-risk customers</strong>'
            f" · {prediction_reviews} predictions need human review in this demo snapshot.</div>",
            unsafe_allow_html=True,
        )
        render_priority_queue(snapshot)
        middle_left, middle_right = st.columns([1, 1.15], gap="large")
        with middle_left:
            render_distribution(snapshot)
        with middle_right:
            render_review(snapshot)
        lower_left, lower_right = st.columns([1.25, 0.85], gap="large")
        with lower_left:
            render_activity(snapshot)
        with lower_right:
            render_model_health(snapshot)
