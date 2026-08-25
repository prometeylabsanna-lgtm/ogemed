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

    Зміна пароля в UI на Vercel не тримається: /tmp SQLite ефемерний і
    копіюється з білду. Задавайте DEMO_ADMIN_PASSWORD у Vercel → Redeploy.
    """
    if not is_vercel_lambda():
        return
    from django.contrib.auth import get_user_model

    User = get_user_model()
    password = demo_admin_password()
    user, _ = User.objects.get_or_create(
        username="admin",
        defaults={
            "email": "admin@ogemed.local",
            "is_staff": True,
            "is_superuser": True,
        },
    )
    # Синхронізуємо з env на кожному cold start — інакше різні /tmp інстанси
    # матимуть різні паролі після «Змінити пароль» в адмінці.
    user.set_password(password)
    user.is_staff = True
    user.is_superuser = True
    user.is_active = True
    user.save(update_fields=["password", "is_staff", "is_superuser", "is_active"])
