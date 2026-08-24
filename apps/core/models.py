from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.fields import OptimizedImageField
from apps.core.image_processing import MAX_SIDE_HERO, MAX_SIDE_LOGO


class SiteSettings(models.Model):
    """Singleton site settings (pk=1). API secrets must stay in env, never here."""

    logo = OptimizedImageField(
        _("Логотип"),
        upload_to="site/",
        blank=True,
        help_text=_("PNG/SVG з прозорим фоном. Порожньо = логотип із static/img/logo.png"),
        max_side=MAX_SIDE_LOGO,
        allow_svg=True,
    )
    phone = models.CharField(_("Телефон"), max_length=32, blank=True)
    email = models.EmailField(_("Email"), blank=True)
    manager_email = models.EmailField(_("Email менеджера"), blank=True)
    address_uk = models.CharField(_("Адреса (UK)"), max_length=255, blank=True)
    address_ru = models.CharField(_("Адреса (RU)"), max_length=255, blank=True)
    work_hours_uk = models.CharField(_("Години роботи (UK)"), max_length=255, blank=True)
    work_hours_ru = models.CharField(_("Години роботи (RU)"), max_length=255, blank=True)
    map_embed_url = models.TextField(
        _("Карта Google"),
        blank=True,
        help_text=_(
            "Вставте коротке посилання Google Maps (maps.app.goo.gl/…) "
            "або повний HTML iframe — сайт сам зробить embed."
        ),
    )
    map_latitude = models.DecimalField(
        _("Широта (застаріле)"),
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        editable=False,
    )
    map_longitude = models.DecimalField(
        _("Довгота (застаріле)"),
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        editable=False,
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
        from apps.core.map_embed import normalize_map_embed

        self.map_embed_url = normalize_map_embed(self.map_embed_url)
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


class SiteBlock(models.Model):
    """Один ключ контенту (page, key) — текст / фото / url."""

    class ContentType(models.TextChoices):
        TEXT = "text", _("Текст")
        IMAGE = "image", _("Фото")
        URL = "url", _("URL")

    class Page(models.TextChoices):
        HOME = "home", _("Головна")
        CATALOG = "catalog", _("Каталог")
        ABOUT = "about", _("Про нас")
        SHIPPING = "shipping", _("Доставка")
        CONTACTS = "contacts", _("Контакти")
        SITE = "site", _("Сайт")

    page = models.CharField(max_length=32, choices=Page.choices, verbose_name=_("Сторінка"))
    key = models.CharField(max_length=64, verbose_name=_("Ключ блоку"))
    label = models.CharField(max_length=128, verbose_name=_("Назва в адмінці"))
    content_type = models.CharField(
        max_length=16,
        choices=ContentType.choices,
        default=ContentType.TEXT,
        verbose_name=_("Тип контенту"),
    )
    text_html = models.TextField(blank=True, verbose_name=_("Текст"))
    image = OptimizedImageField(
        upload_to="blocks/",
        blank=True,
        verbose_name=_("Зображення"),
        max_side=MAX_SIDE_HERO,
    )
    sort_order = models.PositiveSmallIntegerField(default=0, verbose_name=_("Порядок"))
    is_active = models.BooleanField(default=True, verbose_name=_("Активний"))

    class Meta:
        ordering = ["page", "sort_order", "key"]
        verbose_name = _("Блок контенту")
        verbose_name_plural = _("Блоки контенту")
        constraints = [
            models.UniqueConstraint(
                fields=["page", "key"],
                name="unique_site_block_page_key",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.get_page_display()} · {self.label}"

    @property
    def cache_key(self) -> str:
        return f"{self.page}.{self.key}"

    def localized_text(self) -> str:
        from django.utils.translation import get_language

        lang = (get_language() or "uk")[:2]
        uk = getattr(self, "text_html_uk", None)
        ru = getattr(self, "text_html_ru", None)
        if uk is None and ru is None:
            return self.text_html or ""
        uk_val = uk if uk is not None else (self.text_html or "")
        ru_val = ru if ru is not None else ""
        if lang == "ru" and ru_val:
            return ru_val
        return uk_val or ru_val


class HomeHeroSettings(SiteSettings):
    class Meta:
        proxy = True
        verbose_name = _("Головна — Hero")
        verbose_name_plural = _("Головна — Hero")


class HomeBenefitsSettings(SiteSettings):
    class Meta:
        proxy = True
        verbose_name = _("Головна — Переваги")
        verbose_name_plural = _("Головна — Переваги")


class HomeCategoriesSettings(SiteSettings):
    class Meta:
        proxy = True
        verbose_name = _("Головна — Категорії")
        verbose_name_plural = _("Головна — Категорії")


class HomeProductsSettings(SiteSettings):
    class Meta:
        proxy = True
        verbose_name = _("Головна — Товари")
        verbose_name_plural = _("Головна — Товари")


class HomeBrandsSettings(SiteSettings):
    class Meta:
        proxy = True
        verbose_name = _("Головна — Бренди")
        verbose_name_plural = _("Головна — Бренди")


class HomeCareSettings(SiteSettings):
    class Meta:
        proxy = True
        verbose_name = _("Головна — Підбір догляду")
        verbose_name_plural = _("Головна — Підбір догляду")


class HomePromoSettings(SiteSettings):
    class Meta:
        proxy = True
        verbose_name = _("Головна — Промо")
        verbose_name_plural = _("Головна — Промо")


class CatalogSeoSettings(SiteSettings):
    class Meta:
        proxy = True
        verbose_name = _("Каталог — SEO")
        verbose_name_plural = _("Каталог — SEO")


class CatalogFiltersSettings(SiteSettings):
    class Meta:
        proxy = True
        verbose_name = _("Каталог — Фільтри")
        verbose_name_plural = _("Каталог — Фільтри")


class ShippingMethodsSettings(SiteSettings):
    class Meta:
        proxy = True
        verbose_name = _("Доставка — Методи")
        verbose_name_plural = _("Доставка — Методи")


class ShippingPaymentSettings(SiteSettings):
    class Meta:
        proxy = True
        verbose_name = _("Доставка — Оплата")
        verbose_name_plural = _("Доставка — Оплата")


class ContactsIntroSettings(SiteSettings):
    class Meta:
        proxy = True
        verbose_name = _("Контакти — Intro")
        verbose_name_plural = _("Контакти — Intro")


class SiteHeaderSettings(SiteSettings):
    class Meta:
        proxy = True
        verbose_name = _("Шапка сайту")
        verbose_name_plural = _("Шапка сайту")


class SiteFooterSettings(SiteSettings):
    class Meta:
        proxy = True
        verbose_name = _("Підвал сайту")
        verbose_name_plural = _("Підвал сайту")
