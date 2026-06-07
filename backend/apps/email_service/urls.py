# File: backend/apps/email_service/urls.py
# Purpose: URL routes for email service APIs.
# App: email_service

from django.urls import path

from .views import EmailTestView


urlpatterns = [
    path("test/", EmailTestView.as_view(), name="email-test"),
]
