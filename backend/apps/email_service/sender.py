# File: backend/apps/email_service/sender.py
# Purpose: SMTP sender for sharing generated login credentials.
# App: email_service

from __future__ import annotations

import os
import smtplib
from email.mime.text import MIMEText

from dotenv import load_dotenv


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))


def _smtp_login_credentials() -> tuple[str | None, str | None]:
    return os.getenv("SENDER_EMAIL"), os.getenv("SENDER_PASS")


def _send_email(to_email: str, subject: str, body: str) -> None:
    sender_email, sender_password = _smtp_login_credentials()
    if not sender_email or not sender_password:
        raise RuntimeError(
            "Missing SENDER_EMAIL or SENDER_PASS in backend/.env."
        )

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = to_email

    with smtplib.SMTP("smtp.gmail.com", 587, timeout=5) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, [to_email], msg.as_string())


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
        "SMTP configuration is working.\n\n"
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
    except smtplib.SMTPAuthenticationError:
        return (
            False,
            "Email not sent: SMTP authentication failed. Use a Gmail App Password.",
        )
    except Exception as exc:
        return False, f"Email not sent: {exc}"


def send_test_email_safe(to_email: str) -> tuple[bool, str]:
    try:
        send_test_email(to_email=to_email)
        return True, "sent"
    except smtplib.SMTPAuthenticationError:
        return (
            False,
            "SMTP authentication failed. Use a Gmail App Password.",
        )
    except Exception as exc:
        return False, str(exc)

