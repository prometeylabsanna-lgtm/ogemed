"""Shared Django settings for OGEMED for you."""
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, []),
)

_env_file = BASE_DIR / ".env"
if _env_file.exists():
    environ.Env.read_env(_env_file)

SECRET_KEY = (
    env("SECRET_KEY", default="vercel-demo-insecure-key-not-for-real-production") or ""
).strip() or "vercel-demo-insecure-key-not-for-real-production"

DEBUG = env("DEBUG")

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])

INSTALLED_APPS = [
    # Unfold — завжди перед django.contrib.admin
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # modeltranslation — перед власними apps
    "modeltranslation",
    "tinymce",
    "django_htmx",
    "django_q",
    "apps.core.apps.CoreConfig",
    "apps.catalog.apps.CatalogConfig",
    "apps.cart",
    "apps.orders",
    "apps.payments",
    "apps.shipping",
    "apps.accounts.apps.AccountsConfig",
    "apps.cms",
    "apps.notify",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.core.context_processors.site_settings",
                "apps.core.context_processors.site_blocks_context",
                "apps.cart.context_processors.cart",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "uk"

LANGUAGES = [
    ("uk", "Українська"),
    ("ru", "Русский"),
]

MODELTRANSLATION_DEFAULT_LANGUAGE = "uk"
MODELTRANSLATION_LANGUAGES = ("uk", "ru")
MODELTRANSLATION_FALLBACK_LANGUAGES = {"default": ("uk", "ru")}

LOCALE_PATHS = [BASE_DIR / "locale"]

TINYMCE_DEFAULT_CONFIG = {
    "height": 400,
    "menubar": False,
    "plugins": "link lists image code",
    "toolbar": "undo redo | bold italic underline | bullist numlist | link image | code",
    "content_css": False,
    "skin": "oxide",
}

TIME_ZONE = "Europe/Kyiv"

USE_I18N = True
USE_TZ = True

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "ogemed-local",
        "TIMEOUT": 60,
    }
}

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

# Версія для {% vstatic %} у проді (у DEBUG використовується mtime файлу)
STATIC_VERSION = env("STATIC_VERSION", default="1")

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "accounts:cabinet"
LOGOUT_REDIRECT_URL = "core:home"

SITE_URL = env("SITE_URL", default="http://127.0.0.1:8000")

# Секретний префікс адмінки (літери/цифри). /admin/ завжди віддає 404.
ADMIN_URL = (env("ADMIN_URL", default="ogm8k2x9p4qh7n") or "ogm8k2x9p4qh7n").strip().strip("/")

# Integration secrets — env only (never SiteSettings / DB / git).
# Порожні значення = graceful degrade (див. apps.core.integrations / checks).
RESEND_API_KEY = env("RESEND_API_KEY", default="")
FROM_EMAIL = env("FROM_EMAIL", default="noreply@example.com")

LIQPAY_PUBLIC_KEY = env("LIQPAY_PUBLIC_KEY", default="")
LIQPAY_PRIVATE_KEY = env("LIQPAY_PRIVATE_KEY", default="")
LIQPAY_SERVER_URL = env("LIQPAY_SERVER_URL", default="")
LIQPAY_SANDBOX = env.bool("LIQPAY_SANDBOX", default=True)

NP_API_KEY = env("NP_API_KEY", default="")
NP_SENDER_REF = env("NP_SENDER_REF", default="")
NP_SENDER_CONTACT_REF = env("NP_SENDER_CONTACT_REF", default="")
NP_SENDER_CITY_REF = env("NP_SENDER_CITY_REF", default="")
NP_SENDER_ADDRESS_REF = env("NP_SENDER_ADDRESS_REF", default="")
NP_SENDER_PHONE = env("NP_SENDER_PHONE", default="")

TELEGRAM_BOT_TOKEN = env("TELEGRAM_BOT_TOKEN", default="")
TELEGRAM_ADMIN_CHAT_ID = env("TELEGRAM_ADMIN_CHAT_ID", default="")

VIBER_AUTH_TOKEN = env("VIBER_AUTH_TOKEN", default="")
VIBER_ADMIN_ID = env("VIBER_ADMIN_ID", default="")

# Notify queue (Django-Q2). False = sync after on_commit (dev / MVP).
NOTIFY_USE_QUEUE = env.bool("NOTIFY_USE_QUEUE", default=False)
REDIS_URL = env("REDIS_URL", default="")

Q_CLUSTER = {
    "name": "ogemed",
    "workers": 2,
    "timeout": 60,
    "retry": 90,
    "queue_limit": 100,
    "bulk": 5,
    "orm": "default",
    "catch_up": False,
}
if REDIS_URL:
    Q_CLUSTER.pop("orm", None)
    Q_CLUSTER["redis"] = REDIS_URL

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        "apps": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "django": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}

# django-unfold — сайдбар; admin_url передаємо явно (не через django.conf.settings)
from apps.core.unfold_sidebar import build_unfold_config  # noqa: E402

UNFOLD = build_unfold_config(admin_url=ADMIN_URL)
