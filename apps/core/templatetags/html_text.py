"""Фільтри виводу CMS/каталог: без сирих тегів на фронті."""
from django import template

from apps.core.html_text import plain_text, richtext_html

register = template.Library()


@register.filter(name="richtext")
def richtext_filter(value) -> str:
    return richtext_html(value)


@register.filter(name="plain_cms")
def plain_cms_filter(value) -> str:
    return plain_text(value)
