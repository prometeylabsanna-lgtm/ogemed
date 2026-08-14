"""Production settings (DigitalOcean Droplet or Vercel + PostgreSQL)."""
import os

from .base import *  # noqa: F401,F403
from .base import BASE_DIR, env

DEBUG = False

_ON_VERCEL = bool(os.environ.get("VERCEL"))
_DEMO_SECRET = "vercel-demo-insecure-key-not-for-real-production"
SECRET_KEY = env("SECRET_KEY", default=_DEMO_SECRET) if _ON_VERCEL else env("SECRET_KEY")

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

if _ON_VERCEL:
    ALLOWED_HOSTS = list(ALLOWED_HOSTS)
    for host in (".vercel.app", os.environ.get("VERCEL_URL", "")):
        if host and host not in ALLOWED_HOSTS:
            ALLOWED_HOSTS.append(host)
    prod_host = os.environ.get("VERCEL_PROJECT_PRODUCTION_URL", "")
    if prod_host and prod_host not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(prod_host)
    if "https://*.vercel.app" not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS = list(CSRF_TRUSTED_ORIGINS) + ["https://*.vercel.app"]
    vercel_url = os.environ.get("VERCEL_URL", "")
    if vercel_url:
        origin = f"https://{vercel_url}"
        if origin not in CSRF_TRUSTED_ORIGINS:
            CSRF_TRUSTED_ORIGINS.append(origin)

_database_url = os.environ.get("DATABASE_URL", "")
if _database_url:
    DATABASES = {"default": env.db("DATABASE_URL")}
    DATABASES["default"]["CONN_MAX_AGE"] = 0 if _ON_VERCEL else 60
    DATABASES["default"]["CONN_HEALTH_CHECKS"] = True
    if _ON_VERCEL:
        DATABASES["default"].setdefault("OPTIONS", {})
        DATABASES["default"]["OPTIONS"].setdefault("sslmode", "require")
elif _ON_VERCEL:
    from config.vercel_sqlite import sqlite_name

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": sqlite_name(),
        }
    }
else:
    DATABASES = {"default": env.db("DATABASE_URL")}

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage",
    },
}

STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_ROOT = env("MEDIA_ROOT", default=str(BASE_DIR / "media"))

AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME", default="")
AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID", default="")
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY", default="")
AWS_S3_ENDPOINT_URL = env("AWS_S3_ENDPOINT_URL", default="")
AWS_S3_REGION_NAME = env("AWS_S3_REGION_NAME", default="auto")
AWS_S3_CUSTOM_DOMAIN = env("AWS_S3_CUSTOM_DOMAIN", default="")
AWS_S3_SIGNATURE_VERSION = "s3v4"
AWS_QUERYSTRING_AUTH = False
AWS_DEFAULT_ACL = None
AWS_S3_FILE_OVERWRITE = False
AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}

if AWS_STORAGE_BUCKET_NAME:
    STORAGES["default"] = {
        "BACKEND": "storages.backends.s3.S3Storage",
    }
    if AWS_S3_CUSTOM_DOMAIN:
        MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/"

SERVE_MEDIA = False

if _ON_VERCEL:
    NOTIFY_USE_QUEUE = False
    SERVE_MEDIA = True
    _vercel_host = os.environ.get("VERCEL_URL", "")
    if _vercel_host:
        SITE_URL = env("SITE_URL", default=f"https://{_vercel_host}")
