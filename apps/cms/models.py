from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import get_language, gettext_lazy as _

from .about_content import AboutContent  # noqa: F401


class CMSPage(models.Model):
    """Informational CMS page with manual uk/ru content fields."""

    slug = models.SlugField(_("Slug"), max_length=120, unique=True)
    page_key = models.CharField(
        _("Ключ сторінки"),
        max_length=64,
        blank=True,
        help_text=_("about, shipping, returns, contacts, privacy, offer"),
    )
    title_uk = models.CharField(_("Заголовок (UK)"), max_length=255)
    title_ru = models.CharField(_("Заголовок (RU)"), max_length=255, blank=True)
    body_uk = models.TextField(_("Текст (UK)"), blank=True)
    body_ru = models.TextField(_("Текст (RU)"), blank=True)
    is_published = models.BooleanField(_("Опубліковано"), default=True)
    sort_order = models.PositiveIntegerField(_("Порядок"), default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("CMS-сторінка")
        verbose_name_plural = _("CMS-сторінки")
        ordering = ["sort_order", "title_uk"]

    def __str__(self) -> str:
        return self.title_uk

    @property
    def title(self) -> str:
        lang = (get_language() or "uk")[:2]
        if lang == "ru" and self.title_ru:
            return self.title_ru
        return self.title_uk

    @property
    def body(self) -> str:
        lang = (get_language() or "uk")[:2]
        if lang == "ru" and self.body_ru:
            return self.body_ru
        return self.body_uk

    def get_absolute_url(self) -> str:
        key_to_name = {
            "about": "cms:about",
            "contacts": "cms:contacts",
            "shipping": "cms:shipping",
            "returns": "cms:returns",
            "privacy": "cms:privacy",
            "offer": "cms:offer",
        }
        name = key_to_name.get(self.page_key)
        if name:
            return reverse(name)
        slug_to_name = {
            "pro-nas": "cms:about",
            "kontakty": "cms:contacts",
            "dostavka-i-oplata": "cms:shipping",
            "povernennya": "cms:returns",
            "polityka-konfidentsiynosti": "cms:privacy",
            "publichna-oferta": "cms:offer",
        }
        return reverse(slug_to_name.get(self.slug, "cms:about"))


class HeroSlide(models.Model):
    title_uk = models.CharField(_("Заголовок (UK)"), max_length=255)
    title_ru = models.CharField(_("Заголовок (RU)"), max_length=255, blank=True)
    subtitle_uk = models.CharField(_("Підзаголовок (UK)"), max_length=255, blank=True)
    subtitle_ru = models.CharField(_("Підзаголовок (RU)"), max_length=255, blank=True)
    cta_label_uk = models.CharField(
        _("CTA (UK)"), max_length=80, blank=True, default="Дивитись"
    )
    cta_label_ru = models.CharField(
        _("CTA (RU)"), max_length=80, blank=True, default="Смотреть"
    )
    cta_url = models.CharField(_("CTA URL"), max_length=255, blank=True, default="/katalog/")
    image = models.ImageField(_("Зображення"), upload_to="hero/", blank=True)
    is_active = models.BooleanField(_("Активний"), default=True)
    sort_order = models.PositiveIntegerField(_("Порядок"), default=0)

    class Meta:
        verbose_name = _("Hero-слайд")
        verbose_name_plural = _("Hero-слайди")
        ordering = ["sort_order", "id"]

    def __str__(self) -> str:
        return self.title_uk

    def _loc(self, base: str) -> str:
        lang = (get_language() or "uk")[:2]
        uk = getattr(self, f"{base}_uk", "") or ""
        ru = getattr(self, f"{base}_ru", "") or ""
        if lang == "ru" and ru:
            return ru
        return uk or ru

    @property
    def title(self) -> str:
        return self._loc("title")

    @property
    def subtitle(self) -> str:
        return self._loc("subtitle")

    @property
    def cta_label(self) -> str:
        return self._loc("cta_label")


class Lead(models.Model):
    class LeadType(models.TextChoices):
        CALLBACK = "callback", _("Передзвоніть мені")
        FEEDBACK = "feedback", _("Зворотний звʼязок")
        STOCK_NOTIFY = "stock_notify", _("Повідомити про надходження")

    lead_type = models.CharField(
        max_length=32, choices=LeadType.choices, default=LeadType.CALLBACK
    )
    name = models.CharField(_("Імʼя"), max_length=120)
    phone = models.CharField(_("Телефон"), max_length=32)
    email = models.EmailField(_("Email"), blank=True)
    message = models.TextField(_("Повідомлення"), blank=True)
    honeypot = models.CharField(max_length=120, blank=True, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="leads",
    )
    is_processed = models.BooleanField(_("Оброблено"), default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Лід")
        verbose_name_plural = _("Ліди")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.name} ({self.phone})"
