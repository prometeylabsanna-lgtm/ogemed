"""Responsive image URLs: thumb + full srcset when thumb exists."""

from __future__ import annotations

from django import template

from apps.core.image_processing import THUMB_MAX_SIDE, thumb_storage_name, thumb_url

register = template.Library()


def _full_url(field_file) -> str:
    if not field_file:
        return ""
    try:
        return field_file.url or ""
    except Exception:
        return ""


@register.inclusion_tag("partials/_responsive_img.html")
def responsive_img(
    field_file,
    alt="",
    class_name="",
    sizes="(max-width: 768px) 45vw, 200px",
    width=300,
    height=400,
    loading="lazy",
    decoding="async",
    fetchpriority="",
    aria_hidden=False,
):
    """Render <img> with thumb-first src and optional srcset."""
    full = _full_url(field_file)
    thumb = thumb_url(field_file) if field_file else ""
    has_thumb = bool(thumb and full and thumb != full)
    src = thumb if has_thumb else full
    srcset = ""
    if has_thumb:
        srcset = f"{thumb} {THUMB_MAX_SIDE}w, {full} 900w"
    return {
        "src": src,
        "srcset": srcset,
        "sizes": sizes if srcset else "",
        "alt": alt,
        "class_name": class_name,
        "width": width,
        "height": height,
        "loading": loading,
        "decoding": decoding,
        "fetchpriority": fetchpriority,
        "aria_hidden": aria_hidden,
    }


@register.simple_tag
def media_thumb_url(field_file) -> str:
    return thumb_url(field_file) if field_file else ""


@register.simple_tag
def media_has_thumb(field_file) -> bool:
    if not field_file:
        return False
    try:
        name = field_file.name
    except Exception:
        return False
    if not name or str(name).lower().endswith(".svg"):
        return False
    thumb = thumb_storage_name(name)
    try:
        return bool(field_file.storage.exists(thumb))
    except Exception:
        return False
