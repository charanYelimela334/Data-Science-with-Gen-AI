# File: frontend/app.py
# Purpose: Streamlit entry point and navigation between frontend pages.
# App: frontend

from __future__ import annotations

import streamlit as st


st.set_page_config(
    page_title="ResumeBoard AI",
    page_icon="📄",
    layout="wide",
)


PAGES = {
    "Upload Resume": "pages/upload.py",
    "Login": "pages/login.py",
    "Verify & Edit Profile": "pages/verify.py",
    "Open-to-Work Board": "pages/profile_board.py",
}


st.sidebar.title("ResumeBoard AI")
selected = st.sidebar.radio("Navigate", list(PAGES.keys()), index=0)

# Streamlit multipage navigation. We immediately switch to the selected page.
st.switch_page(PAGES[selected])

