"""Templatetags для SiteBlock."""
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


def _block(context, page: str, key: str):
    blocks = context.get("site_blocks") or {}
    return blocks.get(f"{page}.{key}")


@register.simple_tag(takes_context=True)
def block_text(context, page: str, key: str, default: str = "") -> str:
    block = _block(context, page, key)
    if block is None:
        return default
    return block.localized_text() or default


@register.simple_tag(takes_context=True)
def section_visible(context, page: str, key: str, default: bool = True) -> bool:
    block = _block(context, page, key)
    if block is None:
        return default
    val = (block.localized_text() or "").strip().lower()
    return val in {"1", "true", "yes"}


@register.simple_tag(takes_context=True)
def block_image_url(context, page: str, key: str) -> str:
    block = _block(context, page, key)
    if block is None or not block.image:
        return ""
    return block.image.url


@register.simple_tag(takes_context=True)
def block_plain(context, page: str, key: str, default: str = "") -> str:
    return block_text(context, page, key, default)
