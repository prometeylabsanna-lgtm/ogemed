"""WSGI config for OGEMED for you."""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings.production" if os.environ.get("VERCEL") else "config.settings.local",
)

application = get_wsgi_application()
