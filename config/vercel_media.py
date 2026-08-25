"""Writable media root on Vercel: seed files from bundle, uploads to /tmp."""
from __future__ import annotations

import os
from pathlib import Path

from django.core.files.storage import FileSystemStorage

from config.vercel_sqlite import is_vercel_lambda

BASE_DIR = Path(__file__).resolve().parent.parent
BUNDLE_MEDIA = BASE_DIR / "media"
RUNTIME_MEDIA = Path("/tmp/ogemed_media")


def media_root() -> str:
    if not is_vercel_lambda():
        return str(BUNDLE_MEDIA)
    RUNTIME_MEDIA.mkdir(parents=True, exist_ok=True)
    return str(RUNTIME_MEDIA)


class VercelMediaStorage(FileSystemStorage):
    """
    Пише в /tmp (єдине writable місце на лямбді).
    Читає спочатку з /tmp, інакше з закоміченого media/ білду.
    """

    def __init__(self, **kwargs):
        kwargs.setdefault("location", media_root())
        kwargs.setdefault("base_url", "/media/")
        super().__init__(**kwargs)
        self.bundle_root = BUNDLE_MEDIA

    def path(self, name: str) -> str:
        runtime = super().path(name)
        if os.path.isfile(runtime):
            return runtime
        bundled = self.bundle_root / name
        if bundled.is_file():
            return str(bundled)
        return runtime

    def exists(self, name: str) -> bool:
        runtime = Path(super().path(name))
        if runtime.is_file():
            return True
        return (self.bundle_root / name).is_file()
