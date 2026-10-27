from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from frontend.streamlit_app.ui.styles import APP_CSS
from frontend.streamlit_app.routes import APP_PAGES


st.set_page_config(
    page_title="ChurnGuard · Retention Control Room",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(APP_CSS, unsafe_allow_html=True)

selected_page = st.navigation(APP_PAGES, position="hidden")
selected_page.run()
