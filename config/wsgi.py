"""WSGI config for OGEMED for you."""
from django.core.wsgi import get_wsgi_application

from config.boot import configure_settings_module

configure_settings_module()

application = get_wsgi_application()
