# File: backend/apps/accounts/urls.py
# Purpose: URL routes for account APIs.
# App: accounts

from django.urls import path

from .views import LoginView, RegisterView


urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
]

