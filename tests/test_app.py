
from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest


PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Test the page that actually contains the customer form.
APP_PATH = (
    PROJECT_ROOT
    / "frontend"
    / "streamlit_app"
    / "pages"
    / "predict.py"
)

PREDICTION_BUTTON_KEY = (
    "FormSubmitter:customer-form-Run model prediction"
)


def page_text(app: AppTest) -> str:
    """Collect rendered text from the Streamlit page."""
    groups = (
        app.markdown,
        app.caption,
        app.success,
        app.info,
        app.warning,
        app.error,
        app.subheader,
        app.title,
    )

    parts: list[str] = []

    for group in groups:
        for element in group:
            value = getattr(element, "value", None)
            if value is not None:
                parts.append(str(value))

    return " ".join(parts)


def open_prediction_page() -> AppTest:
    """Open the customer-analysis page directly."""
    app = AppTest.from_file(
        str(APP_PATH),
        default_timeout=30,
    ).run()

    assert not app.exception, str(app.exception)
    return app


def submit_prediction(app: AppTest) -> None:
    """Submit the customer form using its current button key."""
    app.button(key=PREDICTION_BUTTON_KEY).click().run()
    assert not app.exception, str(app.exception)


def test_happy_path_renders_live_prediction() -> None:
    app = open_prediction_page()

    submit_prediction(app)

    text = page_text(app)

    assert "MLflow registered model" in text
    assert "ChurnGuard-XGBoost-v1" in text
    assert "45%" in text
    assert "Predicted churn risk" in text
    assert "Recommended retention action" in text

    # Live predictions should display SHAP explanations when available,
    # or clearly report that a valid explanation could not be generated.
    assert (
        "Top per-customer SHAP contributions" in text
        or "SHAP could not generate a valid explanation" in text
    )


def test_invalid_input_does_not_predict() -> None:
    app = open_prediction_page()

    # Customer ID is the first text input on the prediction page.
    app.text_input[0].set_value("")

    # Rerun so the empty value is reflected in the form state.
    app.run()

    submit_prediction(app)

    text = page_text(app)

    assert "Prediction not run" in text


def test_service_error_and_retry() -> None:
    app = open_prediction_page()

    # The development-only failure checkbox is inside the form.
    assert len(app.checkbox) > 0
    app.checkbox[-1].check()

    submit_prediction(app)

    text = page_text(app)

    assert "Simulated service failure" in text
    assert "preserved" in text.lower()

    assert any(
        getattr(button, "label", "") == "Retry model prediction"
        for button in app.button
    )
