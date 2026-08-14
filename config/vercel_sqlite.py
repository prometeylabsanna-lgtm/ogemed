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
