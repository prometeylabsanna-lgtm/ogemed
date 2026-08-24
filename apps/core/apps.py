from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"
    label = "core"
    verbose_name = _("Ядро")

    def ready(self) -> None:
        from django.apps import apps

        from . import checks  # noqa: F401

        try:
            apps.get_app_config("django_q").verbose_name = _("Черга задач")
        except LookupError:
            pass

        try:
            from config.vercel_sqlite import ensure_vercel_demo_admin

            ensure_vercel_demo_admin()
        except Exception:
            # migrate / empty DB — ігноруємо
            pass
