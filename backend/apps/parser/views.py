# File: backend/apps/parser/views.py
# Purpose: API endpoint to parse resume and bootstrap user profile.
# App: parser

from __future__ import annotations

import secrets
from typing import Any

from django.db import transaction
from django.utils.dateparse import parse_date
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import User
from apps.email_service.sender import send_credentials_email_safe
from apps.profiles.models import (
    BasicInfo,
    Certification,
    Education,
    Experience,
    Project,
    Skill,
)

from .gpt_extractor import ResumeParsingError, parse_resume_with_gpt
from .pdf_extractor import extract_text_from_pdf


def _safe_list(value: Any) -> list[dict]:
    return value if isinstance(value, list) else []


def _fallback_email(first_name: str | None, last_name: str | None) -> str:
    base = f"{(first_name or 'user').lower()}.{(last_name or 'resume').lower()}"
    return f"{base}.{secrets.token_hex(3)}@resumeboard.local"


def _to_date_or_none(value: Any):
    if not value:
        return None
    if isinstance(value, str):
        return parse_date(value)
    return value


class ParseResumeView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser]

    @transaction.atomic
    def post(self, request):
        resume_file = request.FILES.get("resume")
        if not resume_file:
            return Response(
                {"status": "error", "message": "Missing resume file."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        raw_text = extract_text_from_pdf(resume_file.read())
        if not raw_text:
            return Response(
                {"status": "error", "message": "Could not extract text from PDF."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            parsed = parse_resume_with_gpt(raw_text)
        except ResumeParsingError as exc:
            return Response(
                {"status": "error", "message": str(exc)},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        basic = parsed.get("basic_info") or {}

        first_name = basic.get("first_name")
        last_name = basic.get("last_name")
        email = basic.get("email") or _fallback_email(first_name, last_name)

        if User.objects.filter(email=email).exists():
            email = _fallback_email(first_name, last_name)

        generated_password = secrets.token_urlsafe(10)
        user = User.objects.create_user(email=email, password=generated_password)

        BasicInfo.objects.create(
            user=user,
            first_name=first_name or "",
            last_name=last_name or "",
            phone=basic.get("phone") or "",
            dob=_to_date_or_none(basic.get("dob")),
            location=basic.get("location") or "",
            linkedin=basic.get("linkedin"),
            github=basic.get("github"),
        )

        Skill.objects.bulk_create(
            [
                Skill(
                    user=user,
                    skill_name=s.get("skill_name") or "",
                    level=s.get("level") or Skill.LEVEL_BEGINNER,
                )
                for s in _safe_list(parsed.get("skills"))
                if s.get("skill_name")
            ]
        )
        Experience.objects.bulk_create(
            [
                Experience(
                    user=user,
                    title=e.get("title") or "",
                    company=e.get("company") or "",
                    duration=e.get("duration") or "",
                    description=e.get("description") or "",
                    responsibilities=e.get("responsibilities") or "",
                )
                for e in _safe_list(parsed.get("experience"))
            ]
        )
        Project.objects.bulk_create(
            [
                Project(
                    user=user,
                    title=p.get("title") or "",
                    description=p.get("description") or "",
                    technologies=p.get("technologies") or "",
                    duration=p.get("duration") or "",
                )
                for p in _safe_list(parsed.get("projects"))
            ]
        )
        Education.objects.bulk_create(
            [
                Education(
                    user=user,
                    degree=e.get("degree") or "",
                    institution=e.get("institution") or "",
                    year=e.get("year") or "",
                    cgpa=e.get("cgpa"),
                )
                for e in _safe_list(parsed.get("education"))
            ]
        )
        Certification.objects.bulk_create(
            [
                Certification(
                    user=user,
                    name=c.get("name") or "",
                    issuer=c.get("issuer") or "",
                    year=c.get("year") or "",
                )
                for c in _safe_list(parsed.get("certifications"))
            ]
        )

        email_sent, email_reason = send_credentials_email_safe(email, generated_password)

        message = (
            "Check your email to login."
            if email_sent
            else "Profile created, but credentials email failed. Contact admin."
        )

        return Response(
            {
                "status": "success",
                "message": message,
                "email_sent": email_sent,
                "credentials": (
                    None
                    if email_sent
                    else {"email": email, "password": generated_password}
                ),
                "email_error": None if email_sent else email_reason,
            },
            status=status.HTTP_201_CREATED,
        )

