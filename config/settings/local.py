"""Local development settings."""
from .base import *  # noqa: F401,F403
from .base import env

DEBUG = True

SECRET_KEY = env(
    "SECRET_KEY",
    default="dev-only-insecure-key-do-not-use-in-prod",
)

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["127.0.0.1", "localhost"])

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
