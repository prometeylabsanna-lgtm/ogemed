"""ASGI config for OGEMED for you."""
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings.production" if os.environ.get("VERCEL") else "config.settings.local",
)

application = get_asgi_application()
