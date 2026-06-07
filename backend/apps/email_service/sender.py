# File: backend/apps/email_service/sender.py
# Purpose: Email sender using Resend API for sharing generated login credentials.
# App: email_service

from __future__ import annotations

import os

import resend
from dotenv import load_dotenv


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))


def _send_email(to_email: str, subject: str, body: str) -> None:
    api_key = (os.getenv("RESEND_API_KEY") or "").strip()
    sender_email = os.getenv("SENDER_EMAIL", "onboarding@resend.dev")

    if not api_key:
        raise RuntimeError(
            "Missing RESEND_API_KEY in environment variables."
        )

    resend.api_key = api_key

    resend.Emails.send({
        "from": sender_email,
        "to": [to_email],
        "subject": subject,
        "text": body,
    })


def send_credentials_email(to_email: str, password: str) -> None:
    login_url = os.getenv("APP_LOGIN_URL", "http://localhost:8501")

    subject = "Your ResumeBoard AI Login Credentials"
    body = (
        "Your account has been created from your resume.\n\n"
        f"Email: {to_email}\n"
        f"Password: {password}\n"
        f"Login: {login_url}\n\n"
        "Please log in and verify your profile."
    )

    _send_email(to_email=to_email, subject=subject, body=body)


def send_test_email(to_email: str) -> None:
    subject = "ResumeBoard AI SMTP Test"
    body = (
        "Email configuration is working.\n\n"
        "This is a test email from ResumeBoard AI backend."
    )
    _send_email(to_email=to_email, subject=subject, body=body)


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


def send_test_email_safe(to_email: str) -> tuple[bool, str]:
    try:
        send_test_email(to_email=to_email)
        return True, "sent"
    except Exception as exc:
        return False, str(exc)
