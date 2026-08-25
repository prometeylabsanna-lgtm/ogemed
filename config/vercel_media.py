"""Writable media root on Vercel: seed files from bundle, uploads to /tmp."""
from __future__ import annotations

import mimetypes
import os
from pathlib import Path

from django.core.exceptions import SuspiciousOperation
from django.core.files.storage import FileSystemStorage
from django.http import FileResponse, Http404, HttpRequest, HttpResponseNotModified
from django.utils._os import safe_join
from django.utils.http import http_date
from django.views.static import was_modified_since

from config.vercel_sqlite import is_vercel_lambda

BASE_DIR = Path(__file__).resolve().parent.parent
BUNDLE_MEDIA = BASE_DIR / "media"
RUNTIME_MEDIA = Path("/tmp/ogemed_media")


def media_root() -> str:
    if not is_vercel_lambda():
        return str(BUNDLE_MEDIA)
    RUNTIME_MEDIA.mkdir(parents=True, exist_ok=True)
    return str(RUNTIME_MEDIA)


def resolve_media_path(relative: str) -> Path | None:
    """Шлях до файлу: спочатку /tmp (аплоади), потім media/ з білду."""
    relative = (relative or "").lstrip("/")
    if not relative:
        return None
    for root in (RUNTIME_MEDIA, BUNDLE_MEDIA):
        try:
            full = Path(safe_join(str(root), relative))
        except SuspiciousOperation:
            return None
        if full.is_file():
            return full
    return None


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


def serve_media(request: HttpRequest, path: str):
    """Як django.views.static.serve, але з fallback на media/ білду."""
    full = resolve_media_path(path)
    if full is None:
        raise Http404("Media not found")

    statobj = full.stat()
    if not was_modified_since(
        request.META.get("HTTP_IF_MODIFIED_SINCE"),
        statobj.st_mtime,
        statobj.st_size,
    ):
        return HttpResponseNotModified()

    content_type, encoding = mimetypes.guess_type(str(full))
    content_type = content_type or "application/octet-stream"
    response = FileResponse(full.open("rb"), content_type=content_type)
    response.headers["Last-Modified"] = http_date(statobj.st_mtime)
    if encoding:
        response.headers["Content-Encoding"] = encoding
    response.headers["Cache-Control"] = "public, max-age=86400"
    return response
