
from __future__ import annotations

from html import escape

import streamlit as st

from ..models import (
    CustomerInput,
    DriverDirection,
    PredictionResponse,
    RiskLabel,
)
from .styles import APP_CSS


RISK_STYLE = {
    RiskLabel.LOW: (
        "#247A55",
        "#E3F1E9",
        "LOW RISK",
        "Lower predicted churn risk",
    ),
    RiskLabel.MEDIUM: (
        "#855708",
        "#F7ECD4",
        "REVIEW",
        "Near the operating threshold",
    ),
    RiskLabel.HIGH: (
        "#B13A32",
        "#F8E5E2",
        "HIGH RISK",
        "Prioritize operator review",
    ),
}


def app_shell(active_view: str) -> None:
    """Render shared navigation and identify the connected model."""
    st.markdown(APP_CSS, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("## ChurnGuard")
        st.caption("RETENTION CONTROL ROOM")
        st.divider()
        st.markdown(
            '<nav class="cg-nav" aria-label="Primary navigation">'
            '<a href="/app">Command Center</a>'
            '<a href="/app/predict">Analyze customer</a>'
            '<a href="/app/customers">Customer history</a>'
            '<a href="/app/batch">Batch prediction</a>'
            '<a href="/app/analytics">Analytics</a>'
            '<a href="/app/model">Model</a>'
            '<a href="/app/model-explanations">Model explanations</a>'
            "</nav>",
            unsafe_allow_html=True,
        )
        st.caption(f"ACTIVE · {escape(active_view.upper())}")
        st.divider()
        st.caption("MODEL SOURCE")
        st.markdown("MLflow registered model · ChurnGuard-XGBoost")
        st.caption(
            "Analyze customer uses the registered model. "
            "Other pages may still use demo fixtures."
        )


def page_header() -> None:
    st.markdown(
        '<div class="cg-mobile-brand">'
        "ChurnGuard · Analyze customer</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="cg-kicker">'
        "Customer analysis / first vertical slice</p>",
        unsafe_allow_html=True,
    )
    st.title("Assess a customer’s churn risk")
    st.markdown(
        '<p class="cg-subhead">'
        "Load an approved sample customer, validate the account context, "
        "and review a registered-model risk estimate with a recommended "
        "retention action.</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="cg-demo"><strong>Model estimate.</strong> '
        "Probabilities are produced by the registered XGBoost model. "
        "They are estimates, not confirmed outcomes or proof of causation. "
        "Per-customer feature explanations are shown only when verified "
        "attributions are available.</div>",
        unsafe_allow_html=True,
    )


def empty_result() -> None:
    st.markdown(
        '<div class="cg-empty"><strong>No risk brief yet</strong>'
        "Select a sample customer, review the fields, then run a model "
        "prediction.</div>",
        unsafe_allow_html=True,
    )


def render_prediction(
    result: PredictionResponse,
    customer: CustomerInput,
) -> None:
    """Render a prediction and its available feature explanations."""
    color, soft, badge, context = RISK_STYLE[result.risk_label]

    probability = max(
        0.0,
        min(1.0, float(result.risk_probability)),
    )
    probability_percent = probability * 100

    threshold = max(
        0.0,
        min(1.0, float(result.threshold)),
    )
    threshold_percent = threshold * 100

    probability_display = round(probability_percent)
    threshold_display = f"{threshold_percent:g}%"

    source = (
        "Demo fixture"
        if result.is_demo_data
        else "MLflow registered model"
    )

    scenario_note = (
        "Conflicting retention and risk signals make this a "
        "review-worthy hard case."
        if result.scenario == "hard_case"
        else result.scenario_description
    )

    st.markdown(
        '<div class="cg-result">',
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
<div class="cg-meta">
  <div class="cg-meta-item">
    <span>Customer</span>
    <strong>{escape(str(result.customer_id))}</strong>
  </div>
  <div class="cg-meta-item">
    <span>Source</span>
    <strong>{escape(source)}</strong>
  </div>
  <div class="cg-meta-item">
    <span>Version</span>
    <strong>{escape(str(result.model_version))}</strong>
  </div>
</div>
<div class="cg-risk"
     style="--risk:{color};--risk-soft:{soft};--score:{probability_percent:.2f}%">
  <div class="cg-risk-head">
    <div>
      <div class="cg-score-label">Predicted churn risk</div>
      <div class="cg-score">{probability_display}%</div>
    </div>
    <div class="cg-band">●&nbsp; {escape(badge)}</div>
  </div>
  <div class="cg-meter"
       role="img"
       aria-label="Risk probability {probability_display} percent; decision threshold {threshold_display}">
    <div class="cg-meter-fill"></div>
    <div class="cg-threshold"
         style="left:{threshold_percent:.2f}%"></div>
  </div>
  <div class="cg-meter-note">
    <span>0% lower signal</span>
    <span>{threshold_display} threshold</span>
    <span>100% higher signal</span>
  </div>
  <p class="cg-brief">
    <strong>{escape(context)}.</strong>
    {escape(str(scenario_note))}
  </p>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("### Why this signal?")

    if result.is_demo_data:
        st.caption(
            "This result is marked as demo data. Its driver values "
            "must not be interpreted as live model attributions."
        )
        _render_drivers(result, customer)

    elif result.top_drivers:
        st.caption(
            "Top per-customer SHAP contributions, ranked by absolute "
            "magnitude. Values are raw model-output (log-odds) units, "
            "not percentage-point changes in churn probability."
        )
        _render_drivers(result, customer)

    else:
        st.caption(
            "The registered model produced this probability, "
            "but verified feature attributions are unavailable."
        )
        st.info(
            "SHAP could not generate a valid explanation for this "
            "prediction. The risk score is still available."
        )

    actions = "".join(
        f"<li>{escape(str(action))}</li>"
        for action in result.recommendation.actions
    )

    st.markdown(
        f"""
<div class="cg-action">
  <div class="cg-action-title">Recommended retention action</div>
  <div>{escape(str(result.recommendation.summary))}</div>
  <ul>{actions}</ul>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("### Customer snapshot")
    st.caption(
        f"{customer.tenure} months · "
        f"{customer.contract} contract · "
        f"${customer.monthly_charges:,.2f}/month · "
        f"{customer.internet_service} internet"
    )

    st.markdown("</div>", unsafe_allow_html=True)


def _driver_display(
    feature: str,
    customer: CustomerInput,
) -> tuple[str, str]:
    """Map transformed model feature names to readable customer details."""
    normalized = (
        feature.lower()
        .replace("categorical", "")
        .replace("numeric", "")
        .replace("remainder__", "")
        .replace("cat__", "")
        .replace("num__", "")
        .strip()
    )

    # Map original feature names and one-hot encoded feature names.
    feature_map = [
        (
            "internet service",
            "Internet service",
            customer.internet_service,
        ),
        (
            "monthly charges",
            "Monthly charges",
            f"${customer.monthly_charges:,.2f}/month",
        ),
        (
            "total charges",
            "Total charges",
            f"${customer.total_charges:,.2f}",
        ),
        (
            "senior citizen",
            "Senior citizen",
            "Yes" if str(customer.senior_citizen) in ("1", "True", "true") else "No",
        ),
        ("phone service", "Phone service", customer.phone_service),
        ("multiple lines", "Multiple lines", customer.multiple_lines),
        ("online security", "Online security", customer.online_security),
        ("online backup", "Online backup", customer.online_backup),
        ("device protection", "Device protection", customer.device_protection),
        ("tech support", "Technical support", customer.tech_support),
        ("streaming tv", "Streaming TV", customer.streaming_tv),
        ("streaming movies", "Streaming movies", customer.streaming_movies),
        ("paperless billing", "Paperless billing", customer.paperless_billing),
        ("payment method", "Payment method", customer.payment_method),
        ("dependents", "Dependents", customer.dependents),
        ("partner", "Partner", customer.partner),
        ("gender", "Gender", customer.gender),
        ("contract", "Contract", customer.contract),
        ("tenure", "Customer tenure", f"{customer.tenure} months"),
    ]

    for token, label, value in feature_map:
        if normalized == token or normalized.startswith(token + " "):
            return label, str(value)

    # Fallback for an unrecognized feature.
    readable = " ".join(
        word.capitalize()
        for word in normalized.replace("_", " ").split()
    )
    return readable or feature, "See customer details"


def _render_drivers(
    result: PredictionResponse,
    customer: CustomerInput,
) -> None:
    """Render readable driver names, customer values, and contributions."""
    for index, driver in enumerate(result.top_drivers, start=1):
        raises = driver.direction == DriverDirection.INCREASES
        direction_text = "Raises risk" if raises else "Lowers risk"
        arrow = "↑" if raises else "↓"
        direction_color = "#B13A32" if raises else "#247A55"

        feature_label, customer_value = _driver_display(
            driver.feature,
            customer,
        )

        impact_label = (
            f"SHAP {driver.impact:+.3f}"
            if not result.is_demo_data
            else f"{driver.impact:+.2f}"
        )

        st.markdown(
            f"""
<div class="cg-driver" style="--direction:{direction_color}">
  <div class="cg-rank">{index:02d}</div>
  <div>
    <div class="cg-driver-title">{escape(feature_label)}</div>
    <div class="cg-driver-copy">
      Customer value: {escape(customer_value)}
    </div>
  </div>
  <div class="cg-impact">
    {arrow} {direction_text} · {impact_label}
  </div>
</div>
""",
            unsafe_allow_html=True,
        )
