import pytest
from streamlit.testing.v1 import AppTest

from frontend.streamlit_app.services import ModelServiceError, MockModelService


MODEL_PATH = "frontend/streamlit_app/pages/model.py"


def page_text(app: AppTest) -> str:
    return " ".join(item.value for item in app.markdown)


def test_demo_model_snapshot_uses_fixture_contract() -> None:
    snapshot = MockModelService().snapshot()
    assert snapshot.status == "demo"
    assert snapshot.fixture_service_available is True
    assert snapshot.model_version == "demo-fixture-v1.0.0"
    assert snapshot.threshold == pytest.approx(0.5)
    assert snapshot.is_demo_data is True


def test_model_identity_does_not_invent_trained_artifact_metadata() -> None:
    snapshot = MockModelService().snapshot()
    assert snapshot.selected_model is None
    assert snapshot.model_family is None
    assert snapshot.training_date is None
    assert snapshot.experiment_tag is None
    assert snapshot.feature_count is None
    assert snapshot.engineered_feature_count is None


def test_planned_pipeline_details_come_from_authoritative_specification() -> None:
    snapshot = MockModelService().snapshot()
    assert snapshot.minimum_engineered_features == 5
    assert "Telco Customer Churn" in snapshot.training_data_description
    assert snapshot.serialization_formats == ["joblib", "skops"]
    assert snapshot.calibration_status.startswith("Not evaluated")
    assert snapshot.serialization_status == "No serialized model artifact exists."
    assert snapshot.mlflow_experiment_reference is None


def test_candidate_comparison_is_planned_without_metrics() -> None:
    candidates = MockModelService().snapshot().candidates
    assert [candidate.name for candidate in candidates] == [
        "Majority baseline",
        "Logistic Regression",
        "Random Forest",
        "XGBoost",
    ]
    for candidate in candidates:
        assert candidate.status == "planned"
        assert candidate.accuracy is None
        assert candidate.precision is None
        assert candidate.recall is None
        assert candidate.f1 is None
        assert candidate.roc_auc is None
        assert candidate.pr_auc is None


def test_model_unavailable_state_removes_current_fixture_values() -> None:
    snapshot = MockModelService().snapshot(mode="unavailable")
    assert snapshot.status == "unavailable"
    assert snapshot.fixture_service_available is False
    assert snapshot.model_version is None
    assert snapshot.threshold is None
    assert "No operating threshold" in snapshot.threshold_context
    assert snapshot.candidates


def test_model_malformed_state_uses_safe_error_contract() -> None:
    with pytest.raises(ModelServiceError, match="could not be prepared"):
        MockModelService().snapshot(mode="malformed")


def test_model_page_loads_with_demo_boundary() -> None:
    app = AppTest.from_file(MODEL_PATH, default_timeout=10).run()
    assert not app.exception
    text = page_text(app)
    assert "Frontend demo boundary" in text
    assert "No trained model, completed experiment" in text
    assert "Deterministic fixture contract available" in text


def test_model_page_renders_identity_and_configuration() -> None:
    app = AppTest.from_file(MODEL_PATH, default_timeout=10).run()
    text = page_text(app)
    assert "demo-fixture-v1.0.0" in text
    assert "Selected model" in text
    assert "Training date" in text
    assert "Experiment tag" in text
    assert "Minimum engineered features planned" in text
    assert "No serialized model artifact exists." in text
    assert "No MLflow experiment is connected." in text


def test_model_page_explains_demo_threshold_without_optimization_claim() -> None:
    app = AppTest.from_file(MODEL_PATH, default_timeout=10).run()
    text = page_text(app)
    assert "Current threshold" in text
    assert "50%" in text
    assert "not been selected or optimized" in text


def test_model_page_renders_candidate_table_without_metrics() -> None:
    app = AppTest.from_file(MODEL_PATH, default_timeout=10).run()
    text = page_text(app)
    for name in (
        "Majority baseline",
        "Logistic Regression",
        "Random Forest",
        "XGBoost",
    ):
        assert name in text
    assert "Planned · not trained" in text
    assert "<table>" in text


def test_model_page_marks_future_evidence_unavailable() -> None:
    app = AppTest.from_file(MODEL_PATH, default_timeout=10).run()
    text = page_text(app)
    assert "What is intentionally unavailable" in text
    assert "no global SHAP" in text
    assert "no deployment health" in text
    assert "no accuracy, precision, recall" in text


def test_model_page_unavailable_state_is_explicit() -> None:
    app = AppTest.from_file(MODEL_PATH, default_timeout=10).run()
    app.selectbox(key="model_page_mode").select("Model unavailable").run()
    text = page_text(app)
    assert not app.exception
    assert "No model information is currently available" in text
    assert "Fixture contract</dt><dd>Unavailable" in text
    assert "No current model value" in text


def test_model_page_error_and_recovery() -> None:
    app = AppTest.from_file(MODEL_PATH, default_timeout=10).run()
    app.selectbox(key="model_page_mode").select(
        "Malformed model metadata"
    ).run()
    assert "could not be loaded" in app.error[0].value
    retry = next(
        button for button in app.button if button.label == "Retry demo model context"
    )
    retry.click().run()
    assert not app.error
    assert "Deterministic fixture contract available" in page_text(app)


def test_model_page_navigation_is_registered() -> None:
    app = AppTest.from_file(MODEL_PATH, default_timeout=10).run()
    assert 'href="/app/model"' in page_text(app)
    assert 'href="/app/analytics"' in page_text(app)