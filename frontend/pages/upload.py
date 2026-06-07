# File: frontend/pages/upload.py
# Purpose: UI for uploading a resume PDF and triggering backend parsing.
# App: frontend

from __future__ import annotations

import streamlit as st

from api.client import parse_resume


st.title("Upload Your Resume")
st.write("We'll parse your PDF, generate a profile automatically, and email you login credentials.")


with st.form("upload_form"):
    uploaded_file = st.file_uploader("Upload resume (PDF)", type=["pdf"])
    submit = st.form_submit_button("Parse & Create Account")

if submit:
    if uploaded_file is None:
        st.warning("Please upload a PDF resume first.")
    else:
        with st.spinner("Parsing resume and generating your profile..."):
            try:
                result = parse_resume(uploaded_file)
                message = result.get("message") or "Check your email to login."
                st.success(message)
            except Exception as e:
                st.error(str(e))

