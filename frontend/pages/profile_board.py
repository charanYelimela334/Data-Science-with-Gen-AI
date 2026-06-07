# File: frontend/pages/profile_board.py
# Purpose: Public open-to-work board UI that displays verified users.
# App: frontend

from __future__ import annotations

from typing import Any, Dict, List

import streamlit as st

from api.client import get_board


st.title("Open-to-Work Board")
st.write("A public preview of profiles that have been verified and marked as Open to Work.")


with st.spinner("Loading board..."):
    try:
        users: List[Dict[str, Any]] = get_board()
    except Exception as e:
        st.error(str(e))
        users = []


if not users:
    st.info("No verified profiles found yet.")
else:
    cols_per_row = 3
    for row_start in range(0, len(users), cols_per_row):
        row_users = users[row_start : row_start + cols_per_row]
        cols = st.columns(len(row_users))
        for col, user in zip(cols, row_users):
            with col:
                first_name = user.get("first_name") or ""
                last_name = user.get("last_name") or ""
                location = user.get("location") or ""
                linkedin = user.get("linkedin") or ""
                skills = user.get("skills") or []

                st.subheader(f"{first_name} {last_name}".strip())
                if location:
                    st.caption(location)

                # Skills as "badges" using simple HTML spans.
                if skills:
                    badges_html = " ".join(
                        [
                            f"<span style='display:inline-block;padding:4px 8px;margin:2px;border:1px solid rgba(49,51,63,.2);border-radius:999px;font-size:12px;'>{s}</span>"
                            for s in skills
                        ]
                    )
                    st.markdown(badges_html, unsafe_allow_html=True)
                else:
                    st.caption("No skills listed.")

                if linkedin:
                    st.markdown(f"[LinkedIn]({linkedin})")

                st.markdown("---")

