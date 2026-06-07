# File: backend/apps/parser/urls.py
# Purpose: URL routes for resume parser API.
# App: parser

from django.urls import path

from .views import ParseResumeView


urlpatterns = [
    path("parse/", ParseResumeView.as_view(), name="parse-resume"),
]

