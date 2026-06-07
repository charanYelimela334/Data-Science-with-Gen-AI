# File: frontend/api/client.py
# Purpose: Centralized REST API client for the Streamlit frontend.
# App: frontend

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv


def _load_base_url() -> str:
    # Load APP_API_BASE_URL from frontend/.env (or fallback to local dev).
    # Note: base URL is not a secret; the backend has the actual secrets in its own .env.
    frontend_dir = os.path.dirname(os.path.dirname(__file__))  # .../frontend
    env_path = os.path.join(frontend_dir, ".env")
    load_dotenv(env_path, override=False)
    return (os.getenv("APP_API_BASE_URL") or "http://localhost:8000").rstrip("/")


BASE_URL = _load_base_url()


def _raise_for_api_error(response: requests.Response) -> None:
    try:
        payload = response.json()
        message = payload.get("message") or payload.get("detail") or payload
    except Exception:
        message = response.text

    raise RuntimeError(f"API request failed ({response.status_code}): {message}")


def parse_resume(file_obj: Any) -> Dict[str, Any]:
    """
    POST /api/parse/
    Expects: multipart/form-data with a resume PDF file.
    Returns: backend JSON (typically includes a success message).
    """
    url = f"{BASE_URL}/api/parse/"

    # Streamlit UploadedFile provides .name and can be read as bytes.
    file_name = getattr(file_obj, "name", "resume.pdf")
    file_type = getattr(file_obj, "type", "application/pdf") or "application/pdf"

    # Prefer getvalue() when present (doesn't consume the stream prematurely).
    if hasattr(file_obj, "getvalue"):
        file_bytes = file_obj.getvalue()
    else:
        file_bytes = file_obj.read()

    files = {"resume": (file_name, file_bytes, file_type)}
    response = requests.post(url, files=files, timeout=180)
    if response.status_code >= 400:
        _raise_for_api_error(response)
    return response.json()


def login(email: str, password: str) -> Dict[str, Any]:
    """
    POST /api/auth/login/
    Expects: { "email": "", "password": "" }
    Returns: { "access": "<JWT>", "refresh": "<JWT>", "user_id": 1 }
    """
    url = f"{BASE_URL}/api/auth/login/"
    response = requests.post(
        url,
        json={"email": email, "password": password},
        timeout=30,
        headers={"Content-Type": "application/json"},
    )
    if response.status_code >= 400:
        _raise_for_api_error(response)
    return response.json()


def _auth_headers(token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def get_profile(token: str) -> Dict[str, Any]:
    """
    GET /api/profile/
    Headers: Authorization: Bearer <JWT>
    Returns: full profile JSON.
    """
    url = f"{BASE_URL}/api/profile/"
    response = requests.get(url, headers=_auth_headers(token), timeout=30)
    if response.status_code >= 400:
        _raise_for_api_error(response)
    return response.json()


def update_profile(token: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    PUT /api/profile/update/
    Headers: Authorization: Bearer <JWT>
    Accepts: Full profile JSON with corrections.
    Action: update all profile tables + set status = open_to_work.
    Returns: { "status": "success", "message": "Profile verified!" }
    """
    url = f"{BASE_URL}/api/profile/update/"
    response = requests.put(
        url,
        headers={**_auth_headers(token), "Content-Type": "application/json"},
        json=data,
        timeout=60,
    )
    if response.status_code >= 400:
        _raise_for_api_error(response)
    return response.json()


def get_board() -> List[Dict[str, Any]]:
    """
    GET /api/board/
    Public endpoint.
    Returns: list of open-to-work users.
    """
    url = f"{BASE_URL}/api/board/"
    response = requests.get(url, timeout=30)
    if response.status_code >= 400:
        _raise_for_api_error(response)

    payload = response.json()
    # Allow backend to return either a raw list or { "results": [...] }.
    if isinstance(payload, list):
        return payload
    return payload.get("results") or payload.get("data") or []

