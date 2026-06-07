# File: backend/apps/profiles/models.py
# Purpose: Resume profile data models linked to user.
# App: profiles

from __future__ import annotations

from django.conf import settings
from django.db import models


class BasicInfo(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="basic_info"
    )
    first_name = models.CharField(max_length=120, blank=True, default="")
    last_name = models.CharField(max_length=120, blank=True, default="")
    phone = models.CharField(max_length=30, blank=True, default="")
    dob = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=255, blank=True, default="")
    linkedin = models.URLField(null=True, blank=True)
    github = models.URLField(null=True, blank=True)


class Skill(models.Model):
    LEVEL_BEGINNER = "Beginner"
    LEVEL_INTERMEDIATE = "Intermediate"
    LEVEL_EXPERT = "Expert"
    LEVEL_CHOICES = [
        (LEVEL_BEGINNER, "Beginner"),
        (LEVEL_INTERMEDIATE, "Intermediate"),
        (LEVEL_EXPERT, "Expert"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="skills"
    )
    skill_name = models.CharField(max_length=150)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default=LEVEL_BEGINNER)


class Experience(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="experience"
    )
    title = models.CharField(max_length=200, blank=True, default="")
    company = models.CharField(max_length=200, blank=True, default="")
    duration = models.CharField(max_length=100, blank=True, default="")
    description = models.TextField(blank=True, default="")
    responsibilities = models.TextField(blank=True, default="")


class Project(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="projects"
    )
    title = models.CharField(max_length=200, blank=True, default="")
    description = models.TextField(blank=True, default="")
    technologies = models.CharField(max_length=500, blank=True, default="")
    duration = models.CharField(max_length=100, blank=True, default="")


class Education(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="education"
    )
    degree = models.CharField(max_length=200, blank=True, default="")
    institution = models.CharField(max_length=255, blank=True, default="")
    year = models.CharField(max_length=50, blank=True, default="")
    cgpa = models.CharField(max_length=50, null=True, blank=True)


class Certification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="certifications"
    )
    name = models.CharField(max_length=255, blank=True, default="")
    issuer = models.CharField(max_length=255, blank=True, default="")
    year = models.CharField(max_length=50, blank=True, default="")

