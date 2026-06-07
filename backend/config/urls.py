# File: backend/config/urls.py
# Purpose: Root URL routing for all backend API endpoints.
# App: backend config

from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("apps.parser.urls")),
    path("api/auth/", include("apps.accounts.urls")),
    path("api/", include("apps.profiles.urls")),
    path("api/email/", include("apps.email_service.urls")),
]

