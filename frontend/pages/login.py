# File: frontend/pages/login.py
# Purpose: Login UI that authenticates against Django JWT endpoint.
# App: frontend

from __future__ import annotations

import streamlit as st

from api.client import login


def _go_to_verify_if_authenticated() -> None:
    token = st.session_state.get("token")
    if token:
        st.switch_page("pages/verify.py")


_go_to_verify_if_authenticated()


st.title("Login")
st.write("Enter your email and password to access and verify your profile.")


with st.form("login_form"):
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    submit = st.form_submit_button("Login")

if submit:
    if not email or not password:
        st.warning("Please enter both email and password.")
    else:
        with st.spinner("Logging in..."):
            try:
                result = login(email=email, password=password)
                access_token = result.get("access")
                if not access_token:
                    raise RuntimeError("Login succeeded but no access token was returned.")

                st.session_state["token"] = access_token
                st.success("Logged in successfully.")
                st.switch_page("pages/verify.py")
            except Exception as e:
                st.error(str(e))

