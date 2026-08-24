"""Редаговані секції юридичних / інфо-сторінок."""
from __future__ import annotations

from django.db import models
from django.utils.translation import get_language, gettext_lazy as _


class InfoPageSection(models.Model):
    """Одна секція контенту на сторінках shipping / returns / privacy / offer."""

    class PageKey(models.TextChoices):
        SHIPPING = "shipping", _("Доставка і оплата")
        RETURNS = "returns", _("Повернення")
        PRIVACY = "privacy", _("Конфіденційність")
        OFFER = "offer", _("Оферта")

    class Layout(models.TextChoices):
        CARD = "card", _("Картка (заголовок / підзаголовок / текст)")
        PROSE = "prose", _("Проза (заголовок / текст)")

    page_key = models.CharField(
        _("Сторінка"),
        max_length=32,
        choices=PageKey.choices,
        db_index=True,
    )
    layout = models.CharField(
        _("Макет"),
        max_length=16,
        choices=Layout.choices,
        default=Layout.CARD,
    )
    heading_uk = models.CharField(_("Заголовок (UK)"), max_length=255)
    heading_ru = models.CharField(_("Заголовок (RU)"), max_length=255, blank=True)
    subheading_uk = models.CharField(
        _("Підзаголовок (UK)"),
        max_length=255,
        blank=True,
        help_text=_("Для макета «Картка» — рядок під заголовком."),
    )
    subheading_ru = models.CharField(_("Підзаголовок (RU)"), max_length=255, blank=True)
    body_uk = models.TextField(_("Текст (UK)"), blank=True)
    body_ru = models.TextField(_("Текст (RU)"), blank=True)
    sort_order = models.PositiveIntegerField(_("Порядок"), default=0, db_index=True)
    is_active = models.BooleanField(_("Активна"), default=True)

    class Meta:
        verbose_name = _("Секція інфо-сторінки")
        verbose_name_plural = _("Секції інфо-сторінок")
        ordering = ["page_key", "sort_order", "id"]

    def __str__(self) -> str:
        return f"{self.page_key}: {self.heading_uk}"

    def _loc(self, base: str) -> str:
        lang = (get_language() or "uk")[:2]
        uk = getattr(self, f"{base}_uk", "") or ""
        ru = getattr(self, f"{base}_ru", "") or ""
        if lang == "ru" and ru:
            return ru
        return uk or ru

    @property
    def heading(self) -> str:
        return self._loc("heading")

    @property
    def subheading(self) -> str:
        return self._loc("subheading")

    @property
    def body(self) -> str:
        return self._loc("body")


class InfoPageMeta(models.Model):
    """CTA та бічна замітка (кроки) для інфо-сторінки."""

    page_key = models.CharField(
        _("Сторінка"),
        max_length=32,
        choices=InfoPageSection.PageKey.choices,
        unique=True,
    )
    cta_title_uk = models.CharField(_("CTA заголовок (UK)"), max_length=255, blank=True)
    cta_title_ru = models.CharField(_("CTA заголовок (RU)"), max_length=255, blank=True)
    cta_text_uk = models.TextField(_("CTA текст (UK)"), blank=True)
    cta_text_ru = models.TextField(_("CTA текст (RU)"), blank=True)
    note_title_uk = models.CharField(
        _("Замітка — заголовок (UK)"),
        max_length=255,
        blank=True,
    )
    note_title_ru = models.CharField(
        _("Замітка — заголовок (RU)"),
        max_length=255,
        blank=True,
    )
    note_steps_uk = models.TextField(
        _("Кроки замітки (UK)"),
        blank=True,
        help_text=_("По одному кроку на рядок."),
    )
    note_steps_ru = models.TextField(
        _("Кроки замітки (RU)"),
        blank=True,
        help_text=_("По одному кроку на рядок."),
    )
    note_text_uk = models.TextField(_("Текст замітки (UK)"), blank=True)
    note_text_ru = models.TextField(_("Текст замітки (RU)"), blank=True)

    class Meta:
        verbose_name = _("Мета інфо-сторінки")
        verbose_name_plural = _("Мета інфо-сторінок")

    def __str__(self) -> str:
        return self.page_key

    def _loc(self, base: str) -> str:
        lang = (get_language() or "uk")[:2]
        uk = getattr(self, f"{base}_uk", "") or ""
        ru = getattr(self, f"{base}_ru", "") or ""
        if lang == "ru" and ru:
            return ru
        return uk or ru

    @property
    def cta_title(self) -> str:
        return self._loc("cta_title")

    @property
    def cta_text(self) -> str:
        return self._loc("cta_text")

    @property
    def note_title(self) -> str:
        return self._loc("note_title")

    @property
    def note_text(self) -> str:
        return self._loc("note_text")

    def note_steps(self) -> list[dict[str, str]]:
        raw = self._loc("note_steps")
        return [{"text": line.strip()} for line in raw.splitlines() if line.strip()]
