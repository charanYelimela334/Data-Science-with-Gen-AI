# File: backend/apps/profiles/serializers.py
# Purpose: Serializers for profile models and board response.
# App: profiles

from __future__ import annotations

from rest_framework import serializers

from .models import BasicInfo, Certification, Education, Experience, Project, Skill


class BasicInfoSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    last_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    phone = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    dob = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    location = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    linkedin = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    github = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = BasicInfo
        fields = [
            "first_name",
            "last_name",
            "phone",
            "dob",
            "location",
            "linkedin",
            "github",
        ]


class SkillSerializer(serializers.ModelSerializer):
    skill_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    level = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = Skill
        fields = ["skill_name", "level"]


class ExperienceSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    company = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    duration = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    responsibilities = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )

    class Meta:
        model = Experience
        fields = ["title", "company", "duration", "description", "responsibilities"]


class ProjectSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    technologies = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    duration = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = Project
        fields = ["title", "description", "technologies", "duration"]


class EducationSerializer(serializers.ModelSerializer):
    degree = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    institution = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    year = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    cgpa = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = Education
        fields = ["degree", "institution", "year", "cgpa"]


class CertificationSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    issuer = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    year = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = Certification
        fields = ["name", "issuer", "year"]


class ProfileResponseSerializer(serializers.Serializer):
    basic_info = BasicInfoSerializer(allow_null=True)
    skills = SkillSerializer(many=True)
    experience = ExperienceSerializer(many=True)
    projects = ProjectSerializer(many=True)
    education = EducationSerializer(many=True)
    certifications = CertificationSerializer(many=True)


class ProfileUpdateSerializer(serializers.Serializer):
    basic_info = BasicInfoSerializer()
    skills = SkillSerializer(many=True)
    experience = ExperienceSerializer(many=True)
    projects = ProjectSerializer(many=True)
    education = EducationSerializer(many=True)
    certifications = CertificationSerializer(many=True)


class BoardUserSerializer(serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    location = serializers.CharField()
    skills = serializers.ListField(child=serializers.CharField())
    linkedin = serializers.CharField(allow_null=True)

