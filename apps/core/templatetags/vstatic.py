"""Статика з версією у query (?v=…), щоб браузер не тримав старі CSS/JS.

DEBUG: версія = mtime файлу, тому правки стилів видно без hard-reload.
Prod: версія = settings.STATIC_VERSION (env), змінюється на релізі.
"""
import os

from django import template
from django.conf import settings
from django.contrib.staticfiles import finders
from django.templatetags.static import static

register = template.Library()


def _file_version(path: str) -> str:
    absolute = finders.find(path)
    if not absolute:
        return ""
    try:
        return str(int(os.path.getmtime(absolute)))
    except OSError:
        return ""


@register.simple_tag
def vstatic(path: str) -> str:
    url = static(path)
    if settings.DEBUG:
        version = _file_version(path)
    else:
        version = str(getattr(settings, "STATIC_VERSION", "") or "")
    if not version:
        return url
    separator = "&" if "?" in url else "?"
    return f"{url}{separator}v={version}"
