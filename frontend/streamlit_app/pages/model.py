from __future__ import annotations

import sys
from html import escape
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from frontend.streamlit_app.models import ModelSnapshot
from frontend.streamlit_app.services import ModelServiceError, MockModelService
from frontend.streamlit_app.services.model import ModelMode
from frontend.streamlit_app.ui.components import app_shell


MODE_OPTIONS: dict[str, ModelMode] = {
    "Demo model context": "demo",
    "Model unavailable": "unavailable",
    "Malformed model metadata": "malformed",
}


@st.cache_resource
def get_model_service() -> MockModelService:
    return MockModelService()


def reset_model_mode() -> None:
    st.session_state.model_page_mode = "Demo model context"


def value_or_unavailable(value: str | int | None) -> str:
    return "Not available" if value is None else escape(str(value))


def render_header(snapshot: ModelSnapshot | None, *, failed: bool = False) -> None:
    service = (
        "Model metadata unavailable"
        if failed
        else snapshot.service_status if snapshot else "Model status service"
    )
    source = (
        "Approved demo fixtures + project specification"
        if snapshot
        else "Frontend-only model context"
    )
    st.markdown(
        '<div class="cg-mobile-brand">ChurnGuard · Model</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="cg-kicker">Model intelligence / operational status</p>',
        unsafe_allow_html=True,
    )
    st.title("Model")
    st.markdown(
        '<p class="cg-subhead">Understand what model information is actually '
        "available before relying on predictions, evaluation, or explanations.</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="cg-demo"><strong>Frontend demo boundary.</strong> No trained '
        "model, completed experiment, evaluation result, serialized artifact, "
        "MLflow run, or production deployment is connected.</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
<div class="cc-statusline" aria-label="Model workspace context">
  <div><span>Workspace state</span><strong>Frontend-only · demo metadata</strong></div>
  <div><span>Service</span><strong>{escape(service)}</strong></div>
  <div><span>Source</span><strong>{escape(source)}</strong></div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_operational_status(snapshot: ModelSnapshot) -> None:
    demo = snapshot.status == "demo"
    status_title = (
        "Deterministic fixture contract available"
        if demo
        else "No model information is currently available"
    )
    status_detail = (
        "The accepted customer workflows can read a fixed demo version and "
        "threshold. This is not a trained or production model."
        if demo
        else "The fixture-backed model context is unavailable. Planned pipeline "
        "requirements remain visible below, but no current model value is implied."
    )
    st.subheader("Current operational status")
    st.markdown(
        f"""
<section class="mo-status {'demo' if demo else 'unavailable'}" role="status" aria-label="Current model status">
  <div>
    <span>Current state</span>
    <strong>{escape(status_title)}</strong>
    <p>{escape(status_detail)}</p>
  </div>
  <dl>
    <div><dt>Trained model</dt><dd>Not connected</dd></div>
    <div><dt>Fixture contract</dt><dd>{'Available' if snapshot.fixture_service_available else 'Unavailable'}</dd></div>
    <div><dt>Production status</dt><dd>Not deployed</dd></div>
  </dl>
</section>
""",
        unsafe_allow_html=True,
    )


def render_identity(snapshot: ModelSnapshot) -> None:
    training_date = (
        snapshot.training_date.strftime("%d %b %Y")
        if snapshot.training_date
        else None
    )
    st.subheader("Model identity")
    st.caption(
        "Artifact-backed fields remain unavailable until the later training stage creates them."
    )
    st.markdown(
        f"""
<dl class="mo-identity">
  <div><dt>Selected model</dt><dd>{value_or_unavailable(snapshot.selected_model)}</dd></div>
  <div><dt>Model family</dt><dd>{value_or_unavailable(snapshot.model_family)}</dd></div>
  <div><dt>Model version</dt><dd>{value_or_unavailable(snapshot.model_version)}</dd></div>
  <div><dt>Training date</dt><dd>{value_or_unavailable(training_date)}</dd></div>
  <div><dt>Experiment tag</dt><dd>{value_or_unavailable(snapshot.experiment_tag)}</dd></div>
</dl>
""",
        unsafe_allow_html=True,
    )


def render_threshold(snapshot: ModelSnapshot) -> None:
    threshold = (
        f"{snapshot.threshold * 100:.0f}%"
        if snapshot.threshold is not None
        else "Not available"
    )
    marker = (
        f'<i style="left:{snapshot.threshold * 100:.1f}%"></i>'
        if snapshot.threshold is not None
        else ""
    )
    aria = (
        f"Demo threshold {threshold}"
        if snapshot.threshold is not None
        else "No threshold available"
    )
    st.subheader("Threshold and classification context")
    st.markdown(
        f"""
<section class="mo-threshold" aria-label="{aria}">
  <div>
    <span>Current threshold</span>
    <strong>{threshold}</strong>
    <small>{'Demo fixture marker' if snapshot.threshold is not None else 'No current model value'}</small>
  </div>
  <div>
    <div class="mo-threshold-track">{marker}</div>
    <div class="mo-threshold-labels"><span>0%</span><span>Reference only</span><span>100%</span></div>
    <p>{escape(snapshot.threshold_context)}</p>
  </div>
</section>
""",
        unsafe_allow_html=True,
    )


def render_configuration(snapshot: ModelSnapshot) -> None:
    feature_count = value_or_unavailable(snapshot.feature_count)
    engineered_count = value_or_unavailable(snapshot.engineered_feature_count)
    formats = ", ".join(snapshot.serialization_formats)
    st.subheader("Configuration and artifact status")
    st.caption(
        "Current artifact values are separated from future pipeline requirements."
    )
    st.markdown(
        f"""
<div class="mo-configuration">
  <section aria-labelledby="model-config-heading">
    <h3 id="model-config-heading">Model configuration</h3>
    <dl>
      <div><dt>Feature count</dt><dd>{feature_count}</dd></div>
      <div><dt>Engineered-feature count</dt><dd>{engineered_count}</dd></div>
      <div><dt>Minimum engineered features planned</dt><dd>{snapshot.minimum_engineered_features}</dd></div>
      <div><dt>Calibration</dt><dd>{escape(snapshot.calibration_status)}</dd></div>
    </dl>
  </section>
  <section aria-labelledby="artifact-status-heading">
    <h3 id="artifact-status-heading">Artifacts and experiments</h3>
    <dl>
      <div><dt>Serialization</dt><dd>{escape(snapshot.serialization_status)}</dd></div>
      <div><dt>Planned formats</dt><dd>{escape(formats)}</dd></div>
      <div><dt>MLflow reference</dt><dd>{value_or_unavailable(snapshot.mlflow_experiment_reference)}</dd></div>
      <div><dt>MLflow status</dt><dd>{escape(snapshot.mlflow_status)}</dd></div>
    </dl>
  </section>
</div>
<section class="mo-data-source" aria-labelledby="training-data-heading">
  <h3 id="training-data-heading">Training data description</h3>
  <p><strong>Planned source:</strong> {escape(snapshot.training_data_description)}</p>
  <small>No training dataset has been loaded or measured in this frontend-only stage.</small>
</section>
""",
        unsafe_allow_html=True,
    )


def metric_value(value: float | None) -> str:
    return "—" if value is None else f"{value * 100:.1f}%"


def render_candidates(snapshot: ModelSnapshot) -> None:
    desktop_rows = []
    mobile_rows = []
    for candidate in snapshot.candidates:
        metrics = [
            metric_value(candidate.accuracy),
            metric_value(candidate.precision),
            metric_value(candidate.recall),
            metric_value(candidate.f1),
            metric_value(candidate.roc_auc),
            metric_value(candidate.pr_auc),
        ]
        desktop_rows.append(
            f"""
<tr>
  <th scope="row">{escape(candidate.name)}</th>
  <td>Planned · not trained</td>
  {''.join(f'<td aria-label="Not available">—</td>' for _ in metrics)}
</tr>
"""
        )
        mobile_rows.append(
            f"""
<li class="mo-candidate">
  <strong>{escape(candidate.name)}</strong>
  <span>Planned · not trained</span>
  <p>Accuracy, precision, recall, F1, ROC-AUC, and PR-AUC are not available.</p>
</li>
"""
        )
    st.subheader("Candidate comparison")
    st.caption(
        "The authoritative candidate set is listed without fabricated performance. "
        "Metrics belong to the later training and Evaluation stages."
    )
    st.markdown(
        f"""
<div class="mo-candidate-table">
  <table>
    <caption>Planned model candidate comparison; no metrics are available</caption>
    <thead><tr>
      <th scope="col">Candidate</th><th scope="col">Status</th>
      <th scope="col">Accuracy</th><th scope="col">Precision</th>
      <th scope="col">Recall</th><th scope="col">F1</th>
      <th scope="col">ROC-AUC</th><th scope="col">PR-AUC</th>
    </tr></thead>
    <tbody>{''.join(desktop_rows)}</tbody>
  </table>
</div>
<ul class="mo-mobile-candidates" aria-label="Planned model candidates">
  {''.join(mobile_rows)}
</ul>
""",
        unsafe_allow_html=True,
    )


def render_evidence_boundary() -> None:
    st.subheader("Evidence boundary")
    st.markdown(
        """
<section class="mo-boundary" role="note">
  <strong>What is intentionally unavailable</strong>
  <ul>
    <li><b>Evaluation:</b> no accuracy, precision, recall, F1, ROC-AUC, PR-AUC, confusion matrix, or calibration evidence.</li>
    <li><b>Explanations:</b> no global SHAP, feature importance, or model-level attribution.</li>
    <li><b>Operations:</b> no deployment health, production usage, drift, latency, or uptime data.</li>
  </ul>
  <p>These surfaces remain deferred until their source artifacts exist and their independent slices are proven.</p>
  <a href="/app/model-explanations">Open deterministic explanation preview →</a>
</section>
""",
        unsafe_allow_html=True,
    )


app_shell("Model")
service = get_model_service()

with st.sidebar.expander("Demo state controls", expanded=False):
    selected_mode = st.selectbox(
        "Model data state",
        list(MODE_OPTIONS),
        key="model_page_mode",
        help="Development-only controls for proving model status states.",
    )

try:
    snapshot = service.snapshot(mode=MODE_OPTIONS[selected_mode])
except ModelServiceError:
    render_header(None, failed=True)
    st.error(
        "The demo model metadata could not be loaded. No model or customer data was changed.",
        icon="⚠️",
    )
    st.caption("Return to the approved demo model context and retry.")
    st.button("Retry demo model context", on_click=reset_model_mode)
else:
    render_header(snapshot)
    render_operational_status(snapshot)
    render_identity(snapshot)
    render_threshold(snapshot)
    render_configuration(snapshot)
    render_candidates(snapshot)
    render_evidence_boundary()