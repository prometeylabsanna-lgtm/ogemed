from django.db import models
from django.utils.translation import gettext_lazy as _


class SiteSettings(models.Model):
    """Singleton site settings (pk=1). API secrets must stay in env, never here."""

    logo = models.ImageField(
        _("Логотип"),
        upload_to="site/",
        blank=True,
        help_text=_("PNG/SVG з прозорим фоном. Порожньо = логотип із static/img/logo.png"),
    )
    phone = models.CharField(_("Телефон"), max_length=32, blank=True)
    email = models.EmailField(_("Email"), blank=True)
    manager_email = models.EmailField(_("Email менеджера"), blank=True)
    address_uk = models.CharField(_("Адреса (UK)"), max_length=255, blank=True)
    address_ru = models.CharField(_("Адреса (RU)"), max_length=255, blank=True)
    work_hours_uk = models.CharField(_("Години роботи (UK)"), max_length=255, blank=True)
    work_hours_ru = models.CharField(_("Години роботи (RU)"), max_length=255, blank=True)
    map_embed_url = models.URLField(
        _("URL карти (iframe)"),
        blank=True,
        help_text=_("Посилання для iframe, напр. OpenStreetMap embed"),
    )
    telegram_url = models.URLField(_("Telegram"), blank=True)
    instagram_url = models.URLField(_("Instagram"), blank=True)
    facebook_url = models.URLField(_("Facebook"), blank=True)
    viber_url = models.URLField(_("Viber"), blank=True)
    telegram_consultant_url = models.URLField(
        _("Telegram консультант (FAB)"),
        blank=True,
        help_text=_("Deep-link на чат консультанта"),
    )
    brand_tagline_uk = models.CharField(
        _("Слоган (UK)"),
        max_length=255,
        blank=True,
        default="Косметика з турботою про вас",
    )
    brand_tagline_ru = models.CharField(
        _("Слоган (RU)"),
        max_length=255,
        blank=True,
        default="Косметика с заботой о вас",
    )
    fop_recipient_name = models.CharField(
        _("ФОП: одержувач"),
        max_length=255,
        blank=True,
        help_text=_("ПІБ ФОП або назва для оплати за реквізитами"),
    )
    fop_iban = models.CharField(_("ФОП: IBAN"), max_length=34, blank=True)
    fop_card_number = models.CharField(_("ФОП: номер картки"), max_length=32, blank=True)
    fop_edrpou = models.CharField(
        _("ФОП: ЄДРПОУ / ІПН"),
        max_length=20,
        blank=True,
    )
    updated_at = models.DateTimeField(_("Оновлено"), auto_now=True)

    class Meta:
        verbose_name = _("Налаштування сайту")
        verbose_name_plural = _("Налаштування сайту")

    def __str__(self) -> str:
        return "SiteSettings"

    def save(self, *args, **kwargs) -> None:
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs) -> tuple[int, dict]:
        return 0, {}

    @classmethod
    def load(cls) -> "SiteSettings":
        obj, _created = cls.objects.get_or_create(pk=1)
        return obj

    @property
    def brand_tagline(self) -> str:
        from django.utils.translation import get_language

        lang = (get_language() or "uk")[:2]
        if lang == "ru" and self.brand_tagline_ru:
            return self.brand_tagline_ru
        return self.brand_tagline_uk or self.brand_tagline_ru

    @property
    def address(self) -> str:
        from django.utils.translation import get_language

        lang = (get_language() or "uk")[:2]
        if lang == "ru" and self.address_ru:
            return self.address_ru
        return self.address_uk or self.address_ru

    @property
    def work_hours(self) -> str:
        from django.utils.translation import get_language

        lang = (get_language() or "uk")[:2]
        if lang == "ru" and self.work_hours_ru:
            return self.work_hours_ru
        return self.work_hours_uk or self.work_hours_ru
