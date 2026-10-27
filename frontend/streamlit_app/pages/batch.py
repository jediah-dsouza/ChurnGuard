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
    BatchResult,
    BatchValidationResult,
    PredictionHistoryRow,
    RiskLabel,
)
from frontend.streamlit_app.services import BatchServiceError, MockBatchService
from frontend.streamlit_app.services.mock_batch import DemoBatchMode
from frontend.streamlit_app.routes import CUSTOMER_DETAIL_PAGE
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
DEMO_MODES: dict[str, DemoBatchMode] = {
    "Valid approved batch": "valid",
    "Invalid approved batch": "invalid",
    "Empty approved batch": "empty",
    "Malformed approved batch": "malformed",
}


@st.cache_resource
def get_batch_service() -> MockBatchService:
    return MockBatchService()


def initialize_state() -> None:
    st.session_state.setdefault("batch_validation", None)
    st.session_state.setdefault("batch_result", None)
    st.session_state.setdefault("batch_error", None)


def reset_batch() -> None:
    st.session_state.batch_validation = None
    st.session_state.batch_result = None
    st.session_state.batch_error = None


def validate_demo(service: MockBatchService, mode: DemoBatchMode) -> None:
    st.session_state.batch_validation = service.validate_demo(mode)
    st.session_state.batch_result = None
    st.session_state.batch_error = None


def validate_upload(service: MockBatchService, uploaded_file: object) -> None:
    content = uploaded_file.getvalue()  # type: ignore[attr-defined]
    filename = uploaded_file.name  # type: ignore[attr-defined]
    st.session_state.batch_validation = service.validate_csv(content, filename)
    st.session_state.batch_result = None
    st.session_state.batch_error = None


def run_batch(
    service: MockBatchService,
    validation: BatchValidationResult,
    *,
    fail: bool = False,
) -> None:
    try:
        with st.spinner(
            f"Analyzing {validation.valid_records} deterministic customer records…"
        ):
            result = service.analyze(validation, fail=fail)
    except BatchServiceError:
        st.session_state.batch_result = None
        st.session_state.batch_error = (
            "The demo batch service did not complete the analysis. "
            "The validated dataset is preserved."
        )
    else:
        st.session_state.batch_result = result
        st.session_state.batch_error = None


def render_header() -> None:
    st.markdown(
        '<div class="cg-mobile-brand">ChurnGuard · Batch Prediction</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="cg-kicker">Operations / deterministic batch workspace</p>',
        unsafe_allow_html=True,
    )
    st.title("Batch Prediction")
    st.markdown(
        '<p class="cg-subhead">Validate multiple approved customer fixtures, run '
        "deterministic analysis, and prioritize records for individual inspection.</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="cg-demo"><strong>Frontend demo.</strong> Batch results use only '
        "approved fixture customers and fixed predictions. No backend, trained model, "
        "production activity, or model-performance metric is connected.</div>",
        unsafe_allow_html=True,
    )


def render_schema(service: MockBatchService) -> None:
    with st.expander("CSV schema requirements", expanded=False):
        st.caption(
            "UTF-8 CSV with one header row. Every record must exactly match an approved fixture."
        )
        st.code(", ".join(service.schema_columns()), language=None)


def render_preview(validation: BatchValidationResult) -> None:
    if not validation.preview_rows:
        return
    headers = ["Customer ID", "Tenure", "Contract", "Monthly charges"]
    rows = "".join(
        "<tr>"
        + "".join(
            f"<td>{escape(row[column])}</td>"
            for column in ("customerID", "tenure", "Contract", "MonthlyCharges")
        )
        + "</tr>"
        for row in validation.preview_rows
    )
    st.markdown("#### Dataset preview")
    st.caption("First five rows; only validation-relevant fixture fields are previewed.")
    st.markdown(
        '<div class="bp-preview"><table><caption>Uploaded customer data preview</caption>'
        "<thead><tr>"
        + "".join(f'<th scope="col">{header}</th>' for header in headers)
        + f"</tr></thead><tbody>{rows}</tbody></table></div>",
        unsafe_allow_html=True,
    )


def render_validation(validation: BatchValidationResult) -> None:
    status_copy = {
        "valid": (
            "valid",
            "Dataset ready",
            "All customer records match the approved deterministic fixtures.",
        ),
        "invalid": (
            "invalid",
            "Dataset blocked",
            "Correct every invalid record before running batch analysis.",
        ),
        "empty": (
            "empty",
            "Dataset is empty",
            "Add at least one approved customer record before analysis.",
        ),
        "malformed": (
            "invalid",
            "Dataset cannot be read",
            "Provide a UTF-8 CSV matching the required customer schema.",
        ),
    }
    status_class, title, detail = status_copy[validation.status]
    st.subheader("Validation")
    st.markdown(
        f"""
<section class="bp-validation {status_class}" role="status">
  <div><span>Validation status</span><strong>{escape(title)}</strong><p>{escape(detail)}</p></div>
  <dl>
    <div><dt>Total records</dt><dd>{validation.total_records}</dd></div>
    <div><dt>Valid records</dt><dd>{validation.valid_records}</dd></div>
    <div><dt>Invalid records</dt><dd>{validation.invalid_records}</dd></div>
    <div><dt>Source</dt><dd>{escape(validation.source_name)}</dd></div>
  </dl>
</section>
""",
        unsafe_allow_html=True,
    )
    if validation.issues:
        issues = "".join(
            f"<li><strong>{'Dataset' if issue.row_number is None else f'Row {issue.row_number}'}</strong>"
            f"{' · ' + escape(issue.customer_id) if issue.customer_id else ''}"
            f"<span>{escape(issue.message)}</span></li>"
            for issue in validation.issues
        )
        st.markdown("#### Validation report")
        st.markdown(
            f'<ul class="bp-issues" aria-label="Dataset validation errors">{issues}</ul>',
            unsafe_allow_html=True,
        )
    render_preview(validation)


def row_markup(row: PredictionHistoryRow) -> tuple[str, str]:
    risk_class = RISK_CLASS[row.risk_label]
    risk_label = RISK_LABEL[row.risk_label]
    probability = f"{row.risk_probability * 100:.0f}%"
    desktop = f"""
<tr>
  <th scope="row">{escape(row.customer_id)}</th>
  <td class="bp-probability">{probability}</td>
  <td><span class="cc-risk {risk_class}">● {escape(risk_label)}</span></td>
  <td>{escape(row.top_driver)}</td>
  <td>{row.tenure} mo</td>
  <td>{escape(row.contract)}</td>
</tr>
"""
    mobile = f"""
<li class="bp-result-card">
  <div class="bp-result-head">
    <strong>{escape(row.customer_id)}</strong>
    <span class="cc-risk {risk_class}">● {escape(risk_label)}</span>
  </div>
  <div class="bp-result-signal">
    <div><span>Predicted risk</span><strong>{probability}</strong></div>
    <div><span>Top driver</span><strong>{escape(row.top_driver)}</strong></div>
  </div>
  <p>{row.tenure} months · {escape(row.contract)}</p>
</li>
"""
    return desktop, mobile


def render_results(service: MockBatchService, result: BatchResult) -> None:
    summary = result.summary
    st.subheader("Batch results")
    st.caption(
        "Calculated only from the validated deterministic records in this batch."
    )
    st.markdown(
        f"""
<div class="bp-summary" aria-label="Batch result summary">
  <div><span>Records analyzed</span><strong>{summary.records_analyzed}</strong></div>
  <div><span>High risk</span><strong>{summary.high_risk}</strong></div>
  <div><span>Medium / Watch</span><strong>{summary.medium_risk}</strong></div>
  <div><span>Low risk</span><strong>{summary.low_risk}</strong></div>
  <div><span>Average predicted risk</span><strong>{summary.average_predicted_risk * 100:.1f}%</strong></div>
</div>
""",
        unsafe_allow_html=True,
    )

    total = max(summary.records_analyzed, 1)
    distribution = [
        ("High", summary.high_risk, "high"),
        ("Medium / Watch", summary.medium_risk, "watch"),
        ("Low", summary.low_risk, "low"),
    ]
    bars = "".join(
        f'<div class="bp-dist-row"><div><strong>{label}</strong><span>{count} of {summary.records_analyzed}</span></div>'
        f'<div class="bp-dist-track" aria-label="{label}: {count} of {summary.records_analyzed}">'
        f'<div class="bp-dist-fill {risk_class}" style="width:{count / total * 100:.1f}%"></div></div></div>'
        for label, count, risk_class in distribution
    )
    st.markdown("#### Risk distribution")
    st.markdown(
        f'<div class="bp-distribution">{bars}</div>',
        unsafe_allow_html=True,
    )

    st.markdown("#### Prioritized customers")
    st.caption(
        "Sorted by predicted churn probability, then customer ID. Risk is stated in text and color."
    )
    desktop_rows, mobile_rows = [], []
    for row in result.rows:
        desktop, mobile = row_markup(row)
        desktop_rows.append(desktop)
        mobile_rows.append(mobile)
    st.markdown(
        '<div class="bp-results-table"><table><caption>Prioritized batch customer results</caption>'
        "<thead><tr><th scope=\"col\">Customer ID</th><th scope=\"col\">Probability</th>"
        "<th scope=\"col\">Risk</th><th scope=\"col\">Top driver</th>"
        "<th scope=\"col\">Tenure</th><th scope=\"col\">Contract</th>"
        "</tr></thead><tbody>"
        + "".join(desktop_rows)
        + '</tbody></table></div><ul class="bp-mobile-results" aria-label="Prioritized batch customer results">'
        + "".join(mobile_rows)
        + "</ul>",
        unsafe_allow_html=True,
    )
    st.markdown("#### Inspect analyzed customer")
    st.caption(
        "Open the existing Customer Detail workspace with the selected deterministic fixture."
    )
    inspect_columns = st.columns(len(result.rows))
    for column, row in zip(inspect_columns, result.rows, strict=True):
        with column:
            if st.button(
                f"Inspect {row.customer_id}",
                key=f"batch_inspect_{row.customer_id}",
                use_container_width=True,
            ):
                st.session_state.detail_route_fixture = row.customer_id
                st.switch_page(CUSTOMER_DETAIL_PAGE)
    st.download_button(
        "Download deterministic results CSV",
        data=service.results_csv(result),
        file_name="churnguard-demo-batch-results.csv",
        mime="text/csv",
        use_container_width=False,
    )


app_shell("Batch Prediction")
service = get_batch_service()
initialize_state()
render_header()

with st.sidebar.expander("Demo state controls", expanded=False):
    selected_demo_mode = st.selectbox(
        "Approved batch state",
        list(DEMO_MODES),
        key="batch_demo_mode",
        help="Development-only deterministic datasets for proving validation states.",
    )
    force_failure = st.checkbox(
        "Force one batch service error",
        key="batch_force_failure",
        help="Preserves the validated dataset and exposes the retry flow.",
    )

st.subheader("Dataset")
source = st.selectbox(
    "Dataset source",
    ["Approved demo batch", "Upload CSV"],
    index=None,
    placeholder="Choose a dataset source",
    key="batch_source",
    on_change=reset_batch,
)

if source is None:
    st.markdown(
        '<div class="bp-idle"><strong>No dataset selected</strong>'
        "<p>Choose the approved demo batch or upload a CSV to begin validation.</p></div>",
        unsafe_allow_html=True,
    )
elif source == "Approved demo batch":
    st.markdown(
        '<div class="bp-source"><strong>Approved four-customer demo batch</strong>'
        "<p>Built directly from the four version-controlled customer fixtures.</p></div>",
        unsafe_allow_html=True,
    )
    action_col, download_col = st.columns([1, 1.3])
    with action_col:
        st.button(
            "Load and validate demo batch",
            type="primary",
            on_click=validate_demo,
            args=(service, DEMO_MODES[selected_demo_mode]),
            use_container_width=True,
        )
    with download_col:
        st.download_button(
            "Download approved input CSV",
            data=service.demo_csv(),
            file_name="churnguard-approved-demo-batch.csv",
            mime="text/csv",
            use_container_width=True,
        )
    render_schema(service)
else:
    uploaded = st.file_uploader(
        "Upload customer CSV",
        type=["csv"],
        help="UTF-8 CSV using the approved ChurnGuard customer schema.",
    )
    st.button(
        "Validate uploaded CSV",
        type="primary",
        disabled=uploaded is None,
        on_click=validate_upload if uploaded is not None else None,
        args=(service, uploaded) if uploaded is not None else None,
    )
    st.download_button(
        "Download approved CSV template",
        data=service.demo_csv(),
        file_name="churnguard-approved-demo-batch.csv",
        mime="text/csv",
    )
    render_schema(service)

validation = cast(
    BatchValidationResult | None,
    st.session_state.batch_validation,
)
result = cast(BatchResult | None, st.session_state.batch_result)

if validation is not None:
    render_validation(validation)
    run_disabled = validation.status != "valid"
    if st.button(
        "Run deterministic batch analysis",
        type="primary",
        disabled=run_disabled,
        use_container_width=False,
    ):
        run_batch(service, validation, fail=force_failure)
        st.rerun()

if st.session_state.batch_error:
    st.error(st.session_state.batch_error, icon="⚠️")
    st.caption("Retry uses the same validated dataset; no customer records were changed.")
    if st.button("Retry batch analysis"):
        if validation is not None:
            run_batch(service, validation)
            st.rerun()

if result is not None:
    render_results(service, result)