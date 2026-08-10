"""Shared abstract mixins."""
from django.db import models
from django.utils.translation import get_language, gettext_lazy as _


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(_("Створено"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Оновлено"), auto_now=True)

    class Meta:
        abstract = True


class SeoFieldsMixin(models.Model):
    seo_title = models.CharField(_("SEO title"), max_length=255, blank=True)
    seo_description = models.TextField(_("SEO description"), blank=True)

    class Meta:
        abstract = True


class LocalizedCharMixin(models.Model):
    """Requires concrete name_uk / name_ru fields on subclass."""

    class Meta:
        abstract = True

    def localized(self, field_base: str) -> str:
        lang = (get_language() or "uk")[:2]
        uk = getattr(self, f"{field_base}_uk", "") or ""
        ru = getattr(self, f"{field_base}_ru", "") or ""
        if lang == "ru" and ru:
            return ru
        return uk or ru
