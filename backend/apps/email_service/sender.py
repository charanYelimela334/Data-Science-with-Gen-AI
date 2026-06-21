# File: backend/apps/email_service/sender.py
# Purpose: Email sender using EmailJS API for sharing generated login credentials.
# App: email_service

from __future__ import annotations

import json
import os
import urllib.request
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))


def send_credentials_email(to_email: str, password: str) -> None:
    login_url = os.getenv("APP_LOGIN_URL", "http://localhost:8501")

    service_id = os.getenv("EMAILJS_SERVICE_ID", "").strip()
    template_id = os.getenv("EMAILJS_TEMPLATE_ID", "").strip()
    public_key = os.getenv("EMAILJS_PUBLIC_KEY", "").strip()
    private_key = os.getenv("EMAILJS_PRIVATE_KEY", "").strip()

    if not all([service_id, template_id, public_key, private_key]):
        raise RuntimeError("Missing EmailJS configuration in environment variables.")

    url = "https://api.emailjs.com/api/v1.0/email/send"
    payload = {
        "service_id": service_id,
        "template_id": template_id,
        "user_id": public_key,
        "accessToken": private_key,
        "template_params": {
            "to_email": to_email,
            "password": password,
            "login_url": login_url
        }
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})

    try:
        with urllib.request.urlopen(req) as response:
            if response.status not in (200, 201):
                raise RuntimeError(f"EmailJS returned status: {response.status}")
    except Exception as e:
        raise RuntimeError(f"Failed to send via EmailJS: {e}")


def send_credentials_email_safe(to_email: str, password: str) -> tuple[bool, str]:
    """
    Send email credentials without crashing request flow.
    Returns (sent_ok, reason).
    """
    try:
        send_credentials_email(to_email, password)
        return True, "sent"
    except Exception as exc:
        return False, f"Email not sent: {exc}"
