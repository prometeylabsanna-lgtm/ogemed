"""ImageField з автоконвертацією в WebP, мініатюрами та очищенням старих файлів."""

from __future__ import annotations

import logging

from django import forms
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_delete
from django.utils.translation import gettext_lazy as _

from .image_processing import (
    MAX_SIDE_DEFAULT,
    WEBP_QUALITY,
    is_svg_upload,
    process_upload,
    thumb_storage_name,
)

logger = logging.getLogger(__name__)


class OptimizedImageFormField(forms.ImageField):
    """Дозволяє SVG (якщо allow_svg), інакше стандартна ImageField-валідація."""

    def __init__(self, *args, allow_svg: bool = False, **kwargs):
        self.allow_svg = allow_svg
        super().__init__(*args, **kwargs)

    def to_python(self, data):
        if data in self.empty_values:
            return None
        if self.allow_svg and is_svg_upload(data):
            return data
        if is_svg_upload(data) and not self.allow_svg:
            raise ValidationError(
                _("SVG не дозволено для цього поля. Завантажте JPG або PNG."),
                code="invalid_svg",
            )
        return super().to_python(data)


class OptimizedImageField(models.ImageField):
    """
    При новому завантаженні:
    - растр → WebP (quality=83), EXIF-автоповорот, без метаданих, ресайз вниз;
    - SVG → санітизація (якщо allow_svg);
    - опційна `_thumb.webp` мініатюра;
    - видалення попереднього файлу + thumb при заміні.
    """

    def __init__(
        self,
        *args,
        max_side: int = MAX_SIDE_DEFAULT,
        quality: int = WEBP_QUALITY,
        generate_thumb: bool = True,
        allow_svg: bool = False,
        **kwargs,
    ):
        self.max_side = max_side
        self.quality = quality
        self.generate_thumb = generate_thumb
        self.allow_svg = allow_svg
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.max_side != MAX_SIDE_DEFAULT:
            kwargs["max_side"] = self.max_side
        if self.quality != WEBP_QUALITY:
            kwargs["quality"] = self.quality
        if not self.generate_thumb:
            kwargs["generate_thumb"] = False
        if self.allow_svg:
            kwargs["allow_svg"] = True
        return name, path, args, kwargs

    def formfield(self, **kwargs):
        kwargs.setdefault("form_class", OptimizedImageFormField)
        kwargs.setdefault("allow_svg", self.allow_svg)
        return super().formfield(**kwargs)

    def contribute_to_class(self, cls, name, **kwargs):
        super().contribute_to_class(cls, name, **kwargs)
        if not cls._meta.abstract:
            post_delete.connect(
                self._on_post_delete,
                sender=cls,
                dispatch_uid=f"optimized_image_post_delete_{cls._meta.label}_{name}",
            )

    def pre_save(self, model_instance, add):
        file = getattr(model_instance, self.attname)
        if file and not getattr(file, "_committed", True):
            previous_name = self._previous_name(model_instance, add)
            try:
                main, thumb = process_upload(
                    file,
                    max_side=self.max_side,
                    quality=self.quality,
                    generate_thumb=self.generate_thumb,
                    allow_svg=self.allow_svg,
                    original_name=getattr(file, "name", "") or "image",
                )
            except ValueError as exc:
                raise ValidationError({self.name: str(exc)}) from exc
            except OSError as exc:
                raise ValidationError(
                    {self.name: _("Не вдалося обробити зображення.")}
                ) from exc

            setattr(model_instance, self.attname, main)
            file = getattr(model_instance, self.attname)
            file.save(main.name, main, save=False)

            if thumb is not None:
                thumb_name = thumb_storage_name(file.name)
                try:
                    self.storage.save(thumb_name, thumb)
                except Exception:
                    logger.exception("Failed to save image thumb %s", thumb_name)

            if previous_name and previous_name != file.name:
                self._delete_with_thumb(previous_name)

            return file

        return super().pre_save(model_instance, add)

    def _previous_name(self, model_instance, add) -> str | None:
        if add or not model_instance.pk:
            return None
        try:
            return (
                type(model_instance)
                ._default_manager.filter(pk=model_instance.pk)
                .values_list(self.attname, flat=True)
                .first()
            )
        except Exception:
            return None

    def _delete_with_thumb(self, name: str) -> None:
        if not name:
            return
        try:
            self.storage.delete(name)
        except Exception:
            logger.exception("Failed to delete media file %s", name)
        thumb = thumb_storage_name(name)
        if thumb and thumb != name:
            try:
                self.storage.delete(thumb)
            except Exception:
                logger.exception("Failed to delete thumb %s", thumb)

    def _on_post_delete(self, sender, instance, **kwargs):
        file = getattr(instance, self.attname, None)
        name = getattr(file, "name", None) if file else None
        if name:
            self._delete_with_thumb(name)
