from __future__ import annotations

import sys
from html import escape
from pathlib import Path
from typing import cast

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from frontend.streamlit_app.models import AnalyticsSnapshot
from frontend.streamlit_app.services import (
    AnalyticsServiceError,
    MockAnalyticsService,
)
from frontend.streamlit_app.services.analytics import AnalyticsMode, AnalyticsSegment
from frontend.streamlit_app.ui.components import app_shell


SEGMENT_OPTIONS: dict[str, AnalyticsSegment] = {
    "Contract": "contract",
    "Tenure bucket": "tenure_bucket",
    "Internet service": "internet_service",
    "Payment method": "payment_method",
}
MODE_OPTIONS: dict[str, AnalyticsMode] = {
    "Sample analytics": "sample",
    "Empty analytics": "empty",
    "Malformed analytics": "malformed",
}


@st.cache_resource
def get_analytics_service() -> MockAnalyticsService:
    return MockAnalyticsService()


def reset_analytics_mode() -> None:
    st.session_state.analytics_mode = "Sample analytics"


def render_header(snapshot: AnalyticsSnapshot | None, *, failed: bool = False) -> None:
    service_status = (
        "Demo analytics unavailable"
        if failed
        else snapshot.service_status if snapshot else "Demo fixture service"
    )
    model_version = snapshot.model_version if snapshot else "demo-fixture-v1.0.0"
    context = (
        snapshot.generated_at.strftime("%d %b %Y · %H:%M UTC")
        if snapshot
        else "Fixed frontend demo context"
    )
    st.markdown(
        '<div class="cg-mobile-brand">ChurnGuard · Analytics</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="cg-kicker">Operations / deterministic risk patterns</p>',
        unsafe_allow_html=True,
    )
    st.title("Analytics")
    st.markdown(
        '<p class="cg-subhead">Compare where predicted risk is concentrated across '
        "the approved sample customers without implying production volume or model quality.</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="cg-demo"><strong>Demo analytics.</strong> Every count, percentage, '
        "date, and segment below is derived from four approved deterministic fixtures. "
        "No production activity or model-performance result is represented.</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
<div class="cc-statusline" aria-label="Analytics context">
  <div><span>Model state</span><strong>{escape(model_version)} · demo only</strong></div>
  <div><span>Service</span><strong>{escape(service_status)}</strong></div>
  <div><span>Fixture snapshot</span><strong>{escape(context)}</strong></div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_summary(snapshot: AnalyticsSnapshot) -> None:
    average = (
        "Not available"
        if snapshot.average_predicted_risk is None
        else f"{snapshot.average_predicted_risk * 100:.1f}%"
    )
    high_rate = (
        "Not available"
        if snapshot.high_risk_rate is None
        else f"{snapshot.high_risk_rate * 100:.1f}%"
    )
    st.subheader("Snapshot measures")
    st.caption("Connected measures from the current four-customer fixture snapshot.")
    st.markdown(
        f"""
<div class="an-summary" aria-label="Analytics snapshot measures">
  <div><span>Prediction volume</span><strong>{snapshot.predictions_analyzed}</strong><small>approved fixture results</small></div>
  <div><span>Average predicted risk</span><strong>{average}</strong><small>arithmetic mean</small></div>
  <div><span>High-risk rate</span><strong>{high_rate}</strong><small>High label share</small></div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_distribution(snapshot: AnalyticsSnapshot) -> None:
    total = max(snapshot.predictions_analyzed, 1)
    values = [
        ("High", snapshot.distribution.high, "high"),
        ("Medium / Watch", snapshot.distribution.medium, "watch"),
        ("Low", snapshot.distribution.low, "low"),
    ]
    rows = "".join(
        f"""
<div class="an-bar-row">
  <div><strong>{label}</strong><span>{count} of {snapshot.predictions_analyzed}</span></div>
  <div class="an-bar-track" aria-label="{label}: {count} of {snapshot.predictions_analyzed} customers">
    <div class="an-bar-fill {risk_class}" style="width:{count / total * 100:.1f}%"></div>
  </div>
</div>
"""
        for label, count, risk_class in values
    )
    st.subheader("Risk-band distribution")
    st.caption("Direct counts make the small deterministic sample explicit.")
    st.markdown(
        f'<section class="an-panel" aria-label="Risk-band distribution">{rows}</section>',
        unsafe_allow_html=True,
    )


def render_volume(snapshot: AnalyticsSnapshot) -> None:
    max_count = max(
        (point.prediction_count for point in snapshot.volume_over_time),
        default=1,
    )
    rows = "".join(
        f"""
<div class="an-volume-row">
  <time datetime="{point.day.isoformat()}">{point.day.strftime("%d %b %Y")}</time>
  <div class="an-volume-track" aria-label="{point.prediction_count} predictions on {point.day.strftime('%d %B %Y')}">
    <div style="width:{point.prediction_count / max_count * 100:.1f}%"></div>
  </div>
  <strong>{point.prediction_count}</strong>
</div>
"""
        for point in snapshot.volume_over_time
    )
    st.subheader("Prediction volume over time")
    st.caption(
        "Fixture prediction count by supplied date; one date is available in the source."
    )
    st.markdown(
        f'<section class="an-panel" aria-label="Prediction volume over time">{rows}</section>',
        unsafe_allow_html=True,
    )


def render_outcomes(snapshot: AnalyticsSnapshot) -> None:
    st.subheader("Prediction success / failure")
    st.markdown(
        f"""
<section class="an-unavailable" role="note" aria-label="Prediction outcome availability">
  <strong>Rate not available</strong>
  <p>{escape(snapshot.prediction_outcomes_note)}</p>
</section>
""",
        unsafe_allow_html=True,
    )


def render_segments(snapshot: AnalyticsSnapshot) -> None:
    desktop_rows = []
    mobile_rows = []
    for row in snapshot.segment_rows:
        average = f"{row.average_predicted_risk * 100:.1f}%"
        high_share = f"{row.high_risk_share * 100:.1f}%"
        desktop_rows.append(
            f"""
<tr>
  <th scope="row">{escape(row.segment_value)}</th>
  <td>{row.customer_count}</td>
  <td class="an-probability">{average}</td>
  <td>{row.high_risk_count}</td>
  <td>{high_share}</td>
</tr>
"""
        )
        mobile_rows.append(
            f"""
<li class="an-segment-card">
  <div><strong>{escape(row.segment_value)}</strong><span>{row.customer_count} customer{'s' if row.customer_count != 1 else ''}</span></div>
  <dl>
    <div><dt>Average predicted risk</dt><dd>{average}</dd></div>
    <div><dt>High-risk customers</dt><dd>{row.high_risk_count}</dd></div>
    <div><dt>High-risk share</dt><dd>{high_share}</dd></div>
  </dl>
</li>
"""
        )

    if snapshot.segment_insight:
        st.markdown(
            f'<div class="an-insight" role="status"><strong>Highest average signal</strong>'
            f"<span>{escape(snapshot.segment_insight)}</span></div>",
            unsafe_allow_html=True,
        )
    st.markdown(
        f"""
<div class="an-segment-table">
  <table>
    <caption>Breakdown by {escape(snapshot.segment_dimension)}</caption>
    <thead><tr>
      <th scope="col">{escape(snapshot.segment_dimension)}</th>
      <th scope="col">Customers</th>
      <th scope="col">Average predicted risk</th>
      <th scope="col">High risk</th>
      <th scope="col">High-risk share</th>
    </tr></thead>
    <tbody>{''.join(desktop_rows)}</tbody>
  </table>
</div>
<ul class="an-mobile-segments" aria-label="Breakdown by {escape(snapshot.segment_dimension)}">
  {''.join(mobile_rows)}
</ul>
""",
        unsafe_allow_html=True,
    )


app_shell("Analytics")
service = get_analytics_service()

with st.sidebar.expander("Demo state controls", expanded=False):
    selected_mode = st.selectbox(
        "Analytics data state",
        list(MODE_OPTIONS),
        key="analytics_mode",
        help="Development-only controls for proving supported analytics states.",
    )

initial_segment_label = cast(
    str,
    st.session_state.get("analytics_segment", "Contract"),
)
initial_segment = cast(
    AnalyticsSegment,
    SEGMENT_OPTIONS.get(initial_segment_label, "contract"),
)

try:
    snapshot = service.snapshot(initial_segment, mode=MODE_OPTIONS[selected_mode])
except AnalyticsServiceError:
    render_header(None, failed=True)
    st.error(
        "The demo analytics snapshot could not be loaded. No customer data was changed.",
        icon="⚠️",
    )
    st.caption("Return to the approved sample analytics and retry.")
    st.button("Retry sample analytics", on_click=reset_analytics_mode)
else:
    render_header(snapshot)
    segment_label = st.selectbox(
        "Segment breakdown",
        list(SEGMENT_OPTIONS),
        key="analytics_segment",
        help="Switches the deterministic breakdown without changing the source records.",
    )
    segment = cast(AnalyticsSegment, SEGMENT_OPTIONS[segment_label])
    if segment != initial_segment:
        snapshot = service.snapshot(segment, mode=MODE_OPTIONS[selected_mode])
    if not snapshot.rows:
        st.markdown(
            '<div class="cc-empty"><strong>No analytics data available</strong>'
            "<p>Analyze approved sample customers before comparing risk patterns.</p>"
            '<a href="/app/predict">Analyze a sample customer →</a></div>',
            unsafe_allow_html=True,
        )
    else:
        render_summary(snapshot)
        overview_left, overview_right = st.columns([1, 1], gap="large")
        with overview_left:
            render_distribution(snapshot)
        with overview_right:
            render_volume(snapshot)
        render_outcomes(snapshot)
        st.subheader("Segment breakdown")
        st.caption(
            "Compare only dimensions present in the approved customer fixtures. "
            "Rows are ordered by average predicted risk."
        )
        render_segments(snapshot)