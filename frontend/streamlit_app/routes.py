from __future__ import annotations

from pathlib import Path

import streamlit as st

PAGES_DIR = Path(__file__).resolve().parent / "pages"

COMMAND_CENTER_PAGE = st.Page(
    PAGES_DIR / "command_center.py",
    title="Command Center",
    url_path="command-center",
    default=True,
)
PREDICT_PAGE = st.Page(
    PAGES_DIR / "predict.py",
    title="Analyze customer",
    url_path="predict",
)
CUSTOMERS_PAGE = st.Page(
    PAGES_DIR / "customers.py",
    title="Customer History",
    url_path="customers",
)
CUSTOMER_DETAIL_PAGE = st.Page(
    PAGES_DIR / "customer_detail.py",
    title="Customer Detail",
    url_path="customer-detail",
)
BATCH_PAGE = st.Page(
    PAGES_DIR / "batch.py",
    title="Batch Prediction",
    url_path="batch",
)
ANALYTICS_PAGE = st.Page(
    PAGES_DIR / "analytics.py",
    title="Analytics",
    url_path="analytics",
)
MODEL_PAGE = st.Page(
    PAGES_DIR / "model.py",
    title="Model",
    url_path="model",
)
MODEL_EXPLANATIONS_PAGE = st.Page(
    PAGES_DIR / "model_explanations.py",
    title="Model Explanations",
    url_path="model-explanations",
)

APP_PAGES = [
    COMMAND_CENTER_PAGE,
    PREDICT_PAGE,
    CUSTOMERS_PAGE,
    CUSTOMER_DETAIL_PAGE,
    BATCH_PAGE,
    ANALYTICS_PAGE,
    MODEL_PAGE,
    MODEL_EXPLANATIONS_PAGE,
]