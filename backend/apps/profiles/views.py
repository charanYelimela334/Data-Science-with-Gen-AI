# File: backend/apps/profiles/views.py
# Purpose: Profile retrieval/update and public board endpoints.
# App: profiles

from __future__ import annotations

import logging

from django.db import transaction
from django.utils.dateparse import parse_date
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import User

from .models import BasicInfo, Certification, Education, Experience, Project, Skill
from .serializers import ProfileUpdateSerializer

from apps.parser.rag.vector_store import vector_store

logger = logging.getLogger(__name__)


def _profile_payload(user: User):
    basic = getattr(user, "basic_info", None)
    return {
        "basic_info": {
            "first_name": basic.first_name if basic else "",
            "last_name": basic.last_name if basic else "",
            "phone": basic.phone if basic else "",
            "dob": basic.dob.isoformat() if basic and basic.dob else None,
            "location": basic.location if basic else "",
            "linkedin": basic.linkedin if basic else None,
            "github": basic.github if basic else None,
        },
        "skills": list(user.skills.values("skill_name", "level")),
        "experience": list(
            user.experience.values(
                "title", "company", "duration", "description", "responsibilities"
            )
        ),
        "projects": list(
            user.projects.values("title", "description", "technologies", "duration")
        ),
        "education": list(user.education.values("degree", "institution", "year", "cgpa")),
        "certifications": list(user.certifications.values("name", "issuer", "year")),
    }


class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(_profile_payload(request.user), status=status.HTTP_200_OK)


class ProfileUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def put(self, request):
        serializer = ProfileUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user = request.user

        basic_info = data["basic_info"]
        BasicInfo.objects.update_or_create(
            user=user,
            defaults={
                "first_name": basic_info.get("first_name", ""),
                "last_name": basic_info.get("last_name", ""),
                "phone": basic_info.get("phone", ""),
                "dob": parse_date(basic_info.get("dob")) if basic_info.get("dob") else None,
                "location": basic_info.get("location", ""),
                "linkedin": basic_info.get("linkedin"),
                "github": basic_info.get("github"),
            },
        )

        user.skills.all().delete()
        user.experience.all().delete()
        user.projects.all().delete()
        user.education.all().delete()
        user.certifications.all().delete()

        Skill.objects.bulk_create(
            [
                Skill(
                    user=user,
                    skill_name=(s.get("skill_name") or ""),
                    level=(
                        s.get("level")
                        if s.get("level")
                        in {
                            Skill.LEVEL_BEGINNER,
                            Skill.LEVEL_INTERMEDIATE,
                            Skill.LEVEL_EXPERT,
                        }
                        else Skill.LEVEL_BEGINNER
                    ),
                )
                for s in data["skills"]
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
                for e in data["experience"]
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
                for p in data["projects"]
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
                for e in data["education"]
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
                for c in data["certifications"]
            ]
        )

        user.profile_status = User.STATUS_OPEN_TO_WORK
        user.save(update_fields=["profile_status"])

        try:
            if user.raw_resume_text:
                corrected_json = _profile_payload(user)
                vector_store.add_resume(
                    str(user.id), 
                    user.raw_resume_text, 
                    corrected_json, 
                    verified=True
                )
        except Exception as e:
            logger.warning(f"Failed to add verified resume to vector store: {e}")

        return Response(
            {"status": "success", "message": "Profile verified!"},
            status=status.HTTP_200_OK,
        )


class BoardView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        users = (
            User.objects.filter(profile_status=User.STATUS_OPEN_TO_WORK)
            .select_related("basic_info")
            .prefetch_related("skills")
        )
        response = []
        for user in users:
            basic = getattr(user, "basic_info", None)
            response.append(
                {
                    "first_name": basic.first_name if basic else "",
                    "last_name": basic.last_name if basic else "",
                    "location": basic.location if basic else "",
                    "skills": [s.skill_name for s in user.skills.all()],
                    "linkedin": basic.linkedin if basic else None,
                }
            )
        return Response(response, status=status.HTTP_200_OK)

