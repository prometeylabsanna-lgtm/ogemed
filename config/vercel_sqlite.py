"""SQLite path for Vercel demo: writable /tmp at runtime, project file at build."""
from __future__ import annotations

import os
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
BUNDLE_DB = BASE_DIR / "db.sqlite3"
RUNTIME_DB = Path("/tmp/ogemed.sqlite3")


def is_vercel_lambda() -> bool:
    return bool(os.environ.get("VERCEL")) and bool(
        os.environ.get("VERCEL_REGION") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME")
    )


def demo_admin_password() -> str:
    """Пароль демо-адміна: env DEMO_ADMIN_PASSWORD / ADMIN_PASSWORD, інакше admin."""
    return (
        (os.environ.get("DEMO_ADMIN_PASSWORD") or os.environ.get("ADMIN_PASSWORD") or "admin")
        .strip()
        or "admin"
    )


def sqlite_name() -> str:
    if not is_vercel_lambda():
        return str(BUNDLE_DB)
    if BUNDLE_DB.is_file() and not RUNTIME_DB.is_file():
        shutil.copy(BUNDLE_DB, RUNTIME_DB)
    return str(RUNTIME_DB)


def ensure_vercel_demo_admin() -> None:
    """На лямбді: staff admin з паролем з env (усі інстанси однакові).

    Важно: set_password() лише коли пароль реально інший. Інакше новий hash
    на кожному cold start інвалідує signed-cookie сесію → «викидає» з адмінки.
    """
    if not is_vercel_lambda():
        return
    from django.contrib.auth import get_user_model

    User = get_user_model()
    password = demo_admin_password()
    user, created = User.objects.get_or_create(
        username="admin",
        defaults={
            "email": "admin@ogemed.local",
            "is_staff": True,
            "is_superuser": True,
        },
    )
    update_fields: list[str] = []
    if created or not user.check_password(password):
        user.set_password(password)
        update_fields.append("password")
    if not user.is_staff:
        user.is_staff = True
        update_fields.append("is_staff")
    if not user.is_superuser:
        user.is_superuser = True
        update_fields.append("is_superuser")
    if not user.is_active:
        user.is_active = True
        update_fields.append("is_active")
    if update_fields:
        user.save(update_fields=update_fields)
