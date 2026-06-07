# File: frontend/pages/verify.py
# Purpose: Verify & edit profile UI; protected by JWT access token.
# App: frontend

from __future__ import annotations

import copy
from typing import Any, Dict, List, Optional

import streamlit as st

from api.client import get_profile, update_profile


LEVEL_OPTIONS = ["Beginner", "Intermediate", "Expert"]


def _clean_str(value: Any) -> Optional[str]:
    if value is None:
        return None
    s = str(value).strip()
    return s or None


def _ensure_profile_loaded(token: str) -> None:
    if st.session_state.get("profile_token") == token and st.session_state.get("draft_profile") is not None:
        return

    with st.spinner("Loading your profile..."):
        profile = get_profile(token)

    st.session_state["profile_token"] = token
    # Keep a draft in session state so users can add rows before saving.
    st.session_state["draft_profile"] = copy.deepcopy(profile)


token = st.session_state.get("token")
if not token:
    st.switch_page("pages/login.py")

_ensure_profile_loaded(token)

draft_profile: Dict[str, Any] = st.session_state["draft_profile"]


def _get_section(name: str, default: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    value = draft_profile.get(name)
    if value is None:
        draft_profile[name] = default
    return draft_profile[name]


basic_info: Dict[str, Any] = draft_profile.get("basic_info") or {}
skills = _get_section("skills", [])
experience = _get_section("experience", [])
projects = _get_section("projects", [])
education = _get_section("education", [])
certifications = _get_section("certifications", [])


st.title("Verify & Edit Profile")
st.write("Review your details and submit corrections. This will make your profile visible on the public board.")


if st.button("Reload profile from server", key="reload_profile"):
    st.session_state.pop("draft_profile", None)
    st.session_state.pop("profile_token", None)
    st.rerun()


# Add buttons are outside the form; they mutate the draft so the form can render the new row(s).
col_a, col_b = st.columns(2)
with col_a:
    if st.button("Add Skill", key="add_skill"):
        draft_profile.setdefault("skills", []).append({"skill_name": "", "level": "Beginner"})
        st.rerun()
with col_b:
    if st.button("Add Experience", key="add_exp"):
        draft_profile.setdefault("experience", []).append(
            {"title": "", "company": "", "duration": "", "description": "", "responsibilities": ""}
        )
        st.rerun()

col_c, col_d = st.columns(2)
with col_c:
    if st.button("Add Project", key="add_project"):
        draft_profile.setdefault("projects", []).append({"title": "", "description": "", "technologies": "", "duration": ""})
        st.rerun()
with col_d:
    if st.button("Add Education", key="add_edu"):
        draft_profile.setdefault("education", []).append({"degree": "", "institution": "", "year": "", "cgpa": None})
        st.rerun()

if st.button("Add Certification", key="add_cert"):
    draft_profile.setdefault("certifications", []).append({"name": "", "issuer": "", "year": ""})
    st.rerun()


with st.form("verify_form"):
    st.subheader("Basic Information")

    first_name = st.text_input("First Name", value=basic_info.get("first_name") or "")
    last_name = st.text_input("Last Name", value=basic_info.get("last_name") or "")
    phone = st.text_input("Phone", value=basic_info.get("phone") or "")
    dob = st.text_input("DOB (YYYY-MM-DD)", value=basic_info.get("dob") or "")
    location = st.text_input("Location", value=basic_info.get("location") or "")
    linkedin = st.text_input("LinkedIn URL", value=basic_info.get("linkedin") or "")
    github = st.text_input("GitHub URL", value=basic_info.get("github") or "")

    st.subheader("Skills")
    edited_skills: List[Dict[str, Any]] = []
    if not skills:
        st.caption('No skills found yet. Click "Add Skill" to create one.')
    for i, skill in enumerate(skills):
        skill_name = st.text_input(f"Skill #{i+1} name", value=skill.get("skill_name") or "", key=f"skill_name_{i}")
        level = st.selectbox(
            f"Skill #{i+1} level",
            options=LEVEL_OPTIONS,
            index=max(0, LEVEL_OPTIONS.index(skill.get("level")) if skill.get("level") in LEVEL_OPTIONS else 0),
            key=f"skill_level_{i}",
        )
        edited_skills.append({"skill_name": _clean_str(skill_name), "level": level})

    st.subheader("Experience")
    edited_experience: List[Dict[str, Any]] = []
    if not experience:
        st.caption('No experience found yet. Click "Add Experience" to create one.')
    for i, exp in enumerate(experience):
        title = st.text_input(f"Role #{i+1} title", value=exp.get("title") or "", key=f"exp_title_{i}")
        company = st.text_input(f"Role #{i+1} company", value=exp.get("company") or "", key=f"exp_company_{i}")
        duration = st.text_input(f"Role #{i+1} duration", value=exp.get("duration") or "", key=f"exp_duration_{i}")
        description = st.text_area(f"Role #{i+1} summary", value=exp.get("description") or "", key=f"exp_desc_{i}")
        responsibilities = st.text_area(
            f"Role #{i+1} responsibilities",
            value=exp.get("responsibilities") or "",
            key=f"exp_resp_{i}",
        )
        edited_experience.append(
            {
                "title": _clean_str(title),
                "company": _clean_str(company),
                "duration": _clean_str(duration),
                "description": _clean_str(description),
                "responsibilities": _clean_str(responsibilities),
            }
        )

    st.subheader("Projects")
    edited_projects: List[Dict[str, Any]] = []
    if not projects:
        st.caption('No projects found yet. Click "Add Project" to create one.')
    for i, proj in enumerate(projects):
        title = st.text_input(f"Project #{i+1} title", value=proj.get("title") or "", key=f"proj_title_{i}")
        description = st.text_area(f"Project #{i+1} description", value=proj.get("description") or "", key=f"proj_desc_{i}")
        technologies = st.text_input(
            f"Project #{i+1} technologies (comma-separated)",
            value=proj.get("technologies") or "",
            key=f"proj_tech_{i}",
        )
        duration = st.text_input(f"Project #{i+1} duration", value=proj.get("duration") or "", key=f"proj_duration_{i}")
        edited_projects.append(
            {
                "title": _clean_str(title),
                "description": _clean_str(description),
                "technologies": _clean_str(technologies),
                "duration": _clean_str(duration),
            }
        )

    st.subheader("Education")
    edited_education: List[Dict[str, Any]] = []
    if not education:
        st.caption('No education entries found yet. Click "Add Education" to create one.')
    for i, edu in enumerate(education):
        degree = st.text_input(f"Education #{i+1} degree", value=edu.get("degree") or "", key=f"edu_degree_{i}")
        institution = st.text_input(f"Education #{i+1} institution", value=edu.get("institution") or "", key=f"edu_inst_{i}")
        year = st.text_input(f"Education #{i+1} year", value=edu.get("year") or "", key=f"edu_year_{i}")
        cgpa = st.text_input(f"Education #{i+1} cgpa", value=("" if edu.get("cgpa") is None else edu.get("cgpa")) or "", key=f"edu_cgpa_{i}")
        edited_education.append(
            {"degree": _clean_str(degree), "institution": _clean_str(institution), "year": _clean_str(year), "cgpa": _clean_str(cgpa)}
        )

    st.subheader("Certifications")
    edited_certs: List[Dict[str, Any]] = []
    if not certifications:
        st.caption('No certifications found yet. Click "Add Certification" to create one.')
    for i, cert in enumerate(certifications):
        name = st.text_input(f"Certification #{i+1} name", value=cert.get("name") or "", key=f"cert_name_{i}")
        issuer = st.text_input(f"Certification #{i+1} issuer", value=cert.get("issuer") or "", key=f"cert_issuer_{i}")
        year = st.text_input(f"Certification #{i+1} year", value=cert.get("year") or "", key=f"cert_year_{i}")
        edited_certs.append({"name": _clean_str(name), "issuer": _clean_str(issuer), "year": _clean_str(year)})

    submitted = st.form_submit_button("Save & Verify Profile")

if submitted:
    corrected_data = {
        "basic_info": {
            "first_name": _clean_str(first_name),
            "last_name": _clean_str(last_name),
            "phone": _clean_str(phone),
            "dob": _clean_str(dob),
            "location": _clean_str(location),
            "linkedin": _clean_str(linkedin),
            "github": _clean_str(github),
        },
        "skills": edited_skills,
        "experience": edited_experience,
        "projects": edited_projects,
        "education": edited_education,
        "certifications": edited_certs,
    }

    with st.spinner("Submitting your verified profile..."):
        try:
            result = update_profile(token, corrected_data)
            st.success(result.get("message") or "Profile verified! You are now Open to Work ✅")
            st.balloons()
            # Keep draft intact; user can still edit again if desired.
        except Exception as e:
            st.error(str(e))

