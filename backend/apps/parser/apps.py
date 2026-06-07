# File: backend/apps/parser/apps.py
# Purpose: App config for resume parser module.
# App: parser

from django.apps import AppConfig


class ParserConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.parser"
