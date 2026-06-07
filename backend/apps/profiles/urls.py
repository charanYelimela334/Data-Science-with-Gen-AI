# File: backend/apps/profiles/urls.py
# Purpose: URL routes for profile and board APIs.
# App: profiles

from django.urls import path

from .views import BoardView, ProfileUpdateView, ProfileView


urlpatterns = [
    path("profile/", ProfileView.as_view(), name="profile"),
    path("profile/update/", ProfileUpdateView.as_view(), name="profile-update"),
    path("board/", BoardView.as_view(), name="board"),
]

