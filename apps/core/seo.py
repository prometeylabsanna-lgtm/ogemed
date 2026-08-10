"""SEO helpers — canonical, hreflang, meta from model fields."""
from __future__ import annotations

from django.conf import settings

from apps.core.breadcrumbs import translate_path_for_language


def site_origin() -> str:
    return (settings.SITE_URL or "http://127.0.0.1:8000").rstrip("/")


def absolute_url(path: str) -> str:
    if path.startswith("http://") or path.startswith("https://"):
        return path
    if not path.startswith("/"):
        path = "/" + path
    return site_origin() + path


def canonical_for_request(request, *, path: str | None = None) -> str:
    """Canonical without query string (avoids filter/sort duplicates)."""
    return absolute_url(path or request.path)


def hreflang_map(request, *, path: str | None = None) -> dict[str, str]:
    """Absolute alternate URLs for uk / ru / x-default (no query)."""
    base_path = path or request.path
    uk = translate_path_for_language(base_path, "uk")
    ru = translate_path_for_language(base_path, "ru")
    # Strip query if translate kept it from a full path — path-only here.
    uk = uk.split("?", 1)[0]
    ru = ru.split("?", 1)[0]
    return {
        "uk": absolute_url(uk),
        "ru": absolute_url(ru),
        "x_default": absolute_url(uk),
    }


def seo_from_object(obj, *, fallback_title: str = "", fallback_description: str = "") -> dict:
    title = (getattr(obj, "seo_title", None) or "").strip() or fallback_title
    description = (getattr(obj, "seo_description", None) or "").strip() or fallback_description
    return {
        "page_title": title,
        "meta_description": description[:300] if description else "",
    }
