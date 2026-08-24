"""Shared abstract mixins."""
from django.db import models
from django.utils.translation import get_language, gettext_lazy as _


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(_("Створено"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Оновлено"), auto_now=True)

    class Meta:
        abstract = True


class SeoFieldsMixin(models.Model):
    seo_title_uk = models.CharField(_("SEO title (UK)"), max_length=255, blank=True)
    seo_title_ru = models.CharField(_("SEO title (RU)"), max_length=255, blank=True)
    seo_description_uk = models.TextField(_("SEO description (UK)"), blank=True)
    seo_description_ru = models.TextField(_("SEO description (RU)"), blank=True)

    class Meta:
        abstract = True

    def _seo_localized(self, field_base: str) -> str:
        lang = (get_language() or "uk")[:2]
        uk = getattr(self, f"{field_base}_uk", "") or ""
        ru = getattr(self, f"{field_base}_ru", "") or ""
        if lang == "ru" and ru:
            return ru
        return uk or ru

    @property
    def seo_title(self) -> str:
        return self._seo_localized("seo_title")

    @property
    def seo_description(self) -> str:
        return self._seo_localized("seo_description")


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
