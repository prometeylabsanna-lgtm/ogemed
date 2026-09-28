"""Перед збереженням моделей: прибрати HTML-теги зі звичайних текстів."""
from __future__ import annotations

from django.db.models.signals import pre_save
from django.dispatch import receiver

from .html_text import clean_field_value

_SKIP_APPS = frozenset({"sessions", "contenttypes", "admin"})
_TEXT_TYPES = frozenset({"CharField", "TextField", "SlugField"})


@receiver(pre_save)
def strip_html_from_text_fields(sender, instance, **kwargs) -> None:
    meta = getattr(sender, "_meta", None)
    if meta is None or meta.app_label in _SKIP_APPS:
        return
    for field in meta.concrete_fields:
        if field.get_internal_type() not in _TEXT_TYPES:
            continue
        value = getattr(instance, field.attname, None)
        if not isinstance(value, str) or not value:
            continue
        single_line = field.get_internal_type() != "TextField"
        cleaned = clean_field_value(field.name, value, single_line=single_line)
        if cleaned != value:
            setattr(instance, field.attname, cleaned)
