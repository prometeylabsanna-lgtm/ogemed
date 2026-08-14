"""ASGI config for OGEMED for you."""
from django.core.asgi import get_asgi_application

from config.boot import configure_settings_module

configure_settings_module()

application = get_asgi_application()
