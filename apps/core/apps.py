from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"
    label = "core"
    verbose_name = "Core"

    def ready(self) -> None:
        from . import checks  # noqa: F401

        try:
            from config.vercel_sqlite import ensure_vercel_demo_admin

            ensure_vercel_demo_admin()
        except Exception:
            # migrate / empty DB — ігноруємо
            pass
