# File: backend/config/wsgi.py
# Purpose: WSGI entrypoint for Django backend service.
# App: backend config

import os

from django.core.wsgi import get_wsgi_application


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
application = get_wsgi_application()

