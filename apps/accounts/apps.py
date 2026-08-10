from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.accounts"
    label = "accounts"
    verbose_name = "Accounts"

    def ready(self) -> None:
        from . import signals  # noqa: F401
        from django.db.models.signals import post_migrate

        def _ensure_roles(**kwargs):
            try:
                from .roles import ensure_manager_group

                ensure_manager_group()
            except Exception:
                pass

        post_migrate.connect(
            _ensure_roles,
            dispatch_uid="accounts_ensure_manager_group",
        )
