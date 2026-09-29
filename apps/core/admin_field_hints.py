"""Підмішує help_text / лейбли підказок у поля форм адмінки."""
from __future__ import annotations

from django.db import models
from django.db.models.fields.files import ImageField

from apps.core.admin_guidelines import (
    get_field_label_override,
    get_image_hint,
    get_text_limit_hint,
    get_text_soft_limit,
    IMAGE_FIELD_PROFILES,
)
from apps.core.fields import OptimizedImageField


def _append_help(formfield, hint: str) -> None:
    if not hint:
        return
    existing = str(formfield.help_text or "").strip()
    if hint in existing:
        return
    formfield.help_text = f"{existing} {hint}".strip() if existing else hint


def _resolve_image_profile(db_field: models.Field) -> str:
    name = db_field.name
    if name in IMAGE_FIELD_PROFILES and name != "image":
        return IMAGE_FIELD_PROFILES[name]
    model = getattr(db_field, "model", None)
    model_name = (model.__name__ if model else "").lower()
    if name == "image":
        if "productimage" in model_name or model_name == "product":
            return "product"
        if "hero" in model_name:
            return "hero"
        if "categor" in model_name:
            return "category"
        if "label" in model_name:
            return "label_icon"
        return "block_image"
    return IMAGE_FIELD_PROFILES.get(name, "block_image")


def _is_image_field(db_field: models.Field) -> bool:
    return isinstance(db_field, (OptimizedImageField, ImageField))


def _is_textish_field(db_field: models.Field) -> bool:
    return isinstance(
        db_field,
        (models.CharField, models.TextField, models.SlugField),
    ) and not isinstance(db_field, models.BinaryField)


def apply_admin_field_hints(db_field: models.Field, formfield) -> None:
    """Додає підказки розміру/формату/символів і замінює технічні лейбли."""
    if formfield is None:
        return

    override = get_field_label_override(db_field.name)
    if override:
        formfield.label = override

    if _is_image_field(db_field):
        profile = _resolve_image_profile(db_field)
        hint = get_image_hint(profile)
        existing = str(formfield.help_text or "").strip()
        if not existing:
            formfield.help_text = hint
        elif hint and hint not in existing and "Формат:" not in existing:
            formfield.help_text = f"{existing} {hint}".strip()
        return

    if not _is_textish_field(db_field):
        return

    # Не чіпаємо паролі / службові поля
    if db_field.name in {
        "password",
        "access_token",
        "idempotency_key",
        "search_text",
        "honeypot",
    }:
        return

    max_length = getattr(db_field, "max_length", None)
    hint = get_text_limit_hint(db_field.name, max_length=max_length)
    _append_help(formfield, hint)

    soft = get_text_soft_limit(db_field.name)
    if soft and hasattr(formfield, "widget") and formfield.widget is not None:
        attrs = formfield.widget.attrs
        attrs.setdefault("data-recommend-max", str(soft))
        label = str(formfield.label or db_field.verbose_name or db_field.name)
        attrs.setdefault("data-field-label", label)


class AdminFieldHintsMixin:
    """Підключати першим у MRO ModelAdmin / Form."""

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        apply_admin_field_hints(db_field, formfield)
        return formfield
