"""Vercel build: migrate + demo seed. Unbuffered logs."""
from __future__ import annotations

import os
import sys
import traceback

os.environ["VERCEL"] = "1"
os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings.production"
# Демо-SQLite лише без DATABASE_URL. Якщо в Vercel задано Neon/Postgres — лишаємо.
if not (os.environ.get("DATABASE_URL") or "").strip():
    os.environ.pop("DATABASE_URL", None)
if not (os.environ.get("SECRET_KEY") or "").strip():
    os.environ["SECRET_KEY"] = "vercel-demo-insecure-key-not-for-real-production"


def main() -> None:
    db = "postgres" if (os.environ.get("DATABASE_URL") or "").strip() else "sqlite"
    print(f"vercel_build: migrate ({db})", flush=True)
    from django.core.management import execute_from_command_line

    execute_from_command_line(["manage.py", "migrate", "--noinput"])
    print("vercel_build: seed_demo", flush=True)
    execute_from_command_line(["manage.py", "seed_demo"])
    print("vercel_build: seed_site_blocks", flush=True)
    execute_from_command_line(["manage.py", "seed_site_blocks"])
    print("vercel_build: seed_info_sections", flush=True)
    execute_from_command_line(["manage.py", "seed_info_sections"])
    print("vercel_build: build_static_bundles", flush=True)
    execute_from_command_line(["manage.py", "build_static_bundles"])
    print("vercel_build: collectstatic", flush=True)
    execute_from_command_line(["manage.py", "collectstatic", "--noinput"])
    print("vercel_build: done", flush=True)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        sys.exit(1)
