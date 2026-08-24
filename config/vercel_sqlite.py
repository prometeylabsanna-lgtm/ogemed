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


def sqlite_name() -> str:
    if not is_vercel_lambda():
        return str(BUNDLE_DB)
    if BUNDLE_DB.is_file() and not RUNTIME_DB.is_file():
        shutil.copy(BUNDLE_DB, RUNTIME_DB)
    return str(RUNTIME_DB)


def ensure_vercel_demo_admin() -> None:
    """Якщо на лямбді немає staff — створити admin/admin (після copy БД з білду)."""
    if not is_vercel_lambda():
        return
    from django.contrib.auth import get_user_model

    User = get_user_model()
    if User.objects.filter(is_superuser=True).exists():
        return
    user, _ = User.objects.get_or_create(
        username="admin",
        defaults={
            "email": "admin@ogemed.local",
            "is_staff": True,
            "is_superuser": True,
        },
    )
    user.set_password("admin")
    user.is_staff = True
    user.is_superuser = True
    user.is_active = True
    user.save()
