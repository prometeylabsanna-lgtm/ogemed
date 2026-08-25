from django.db import models
from django.db.models import Min, Q
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
import uuid
from decimal import Decimal

from apps.core.fields import OptimizedImageField
from apps.core.image_processing import MAX_SIDE_LOGO, MAX_SIDE_PRODUCT
from apps.core.mixins import LocalizedCharMixin, SeoFieldsMixin, TimeStampedModel

from .labels import active_labels


class Availability(models.TextChoices):
    IN_STOCK = "in_stock", _("В наявності")
    ON_ORDER = "on_order", _("Під замовлення")
    OUT_OF_STOCK = "out_of_stock", _("Немає в наявності")


class Category(TimeStampedModel, SeoFieldsMixin, LocalizedCharMixin):
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        verbose_name=_("Батьківська категорія"),
    )
    slug = models.SlugField(_("Slug"), max_length=120, unique=True)
    name_uk = models.CharField(_("Назва (UK)"), max_length=255)
    name_ru = models.CharField(_("Назва (RU)"), max_length=255, blank=True)
    image = OptimizedImageField(
        _("Зображення"),
        upload_to="categories/",
        blank=True,
        max_side=MAX_SIDE_PRODUCT,
    )
    description_uk = models.TextField(_("Опис (UK)"), blank=True)
    description_ru = models.TextField(_("Опис (RU)"), blank=True)
    is_active = models.BooleanField(_("Активна"), default=True)
    sort_order = models.PositiveIntegerField(_("Порядок"), default=0)

    class Meta:
        verbose_name = _("Категорія")
        verbose_name_plural = _("Категорії")
        ordering = ["sort_order", "name_uk"]

    def __str__(self) -> str:
        return self.name_uk

    @property
    def name(self) -> str:
        return self.localized("name")

    @property
    def description(self) -> str:
        return self.localized("description")

    def get_absolute_url(self) -> str:
        return reverse("catalog:category", kwargs={"slug": self.slug})

    def get_ancestors(self) -> list["Category"]:
        ancestors: list[Category] = []
        node = self.parent
        while node is not None:
            ancestors.insert(0, node)
            node = node.parent
        return ancestors


class Brand(TimeStampedModel, SeoFieldsMixin, LocalizedCharMixin):
    slug = models.SlugField(_("Slug"), max_length=120, unique=True)
    name_uk = models.CharField(_("Назва (UK)"), max_length=255)
    name_ru = models.CharField(_("Назва (RU)"), max_length=255, blank=True)
    tagline_uk = models.TextField(_("Короткий опис (UK)"), blank=True)
    tagline_ru = models.TextField(_("Короткий опис (RU)"), blank=True)
    description_uk = models.TextField(_("Опис / історія (UK)"), blank=True)
    description_ru = models.TextField(_("Опис / історія (RU)"), blank=True)
    cover_image = OptimizedImageField(
        _("Фото для каталогу"),
        upload_to="brands/covers/",
        blank=True,
        help_text=_("Плитка бренду у фільтрах каталогу."),
        max_side=MAX_SIDE_PRODUCT,
    )
    showcase_image = OptimizedImageField(
        _("Зображення для вітрини на головній"),
        upload_to="brands/showcase/",
        blank=True,
        help_text=_("PNG без фону. Якщо порожнє — візьметься фото для каталогу."),
        max_side=MAX_SIDE_PRODUCT,
    )
    is_featured = models.BooleanField(_("Показувати на головній"), default=False)
    is_active = models.BooleanField(_("Активний"), default=True)
    sort_order = models.PositiveIntegerField(_("Порядок"), default=0)

    class Meta:
        verbose_name = _("Бренд")
        verbose_name_plural = _("Бренди")
        ordering = ["sort_order", "name_uk"]

    def __str__(self) -> str:
        return self.name_uk

    @property
    def name(self) -> str:
        return self.localized("name")

    @property
    def tagline(self) -> str:
        return self.localized("tagline")

    @property
    def description(self) -> str:
        return self.localized("description")

    def get_absolute_url(self) -> str:
        return reverse("catalog:brand_detail", kwargs={"slug": self.slug})

    def _image_file_exists(self, field) -> bool:
        if not field or not getattr(field, "name", None):
            return False
        try:
            return field.storage.exists(field.name)
        except Exception:
            return False

    @property
    def has_cover_image(self) -> bool:
        """True лише якщо файл реально є в storage (не «битий» шлях у БД)."""
        return self._image_file_exists(self.cover_image)

    @property
    def has_showcase_image(self) -> bool:
        return self._image_file_exists(self.showcase_image)

    @property
    def display_cover(self):
        """Обкладинка для вітрини: showcase → cover → None."""
        if self.has_showcase_image:
            return self.showcase_image
        if self.has_cover_image:
            return self.cover_image
        return None


class Attribute(TimeStampedModel, LocalizedCharMixin):
    slug = models.SlugField(_("Slug"), max_length=80, unique=True)
    name_uk = models.CharField(_("Назва (UK)"), max_length=120)
    name_ru = models.CharField(_("Назва (RU)"), max_length=120, blank=True)
    categories = models.ManyToManyField(
        "catalog.Category",
        blank=True,
        related_name="filter_attributes",
        verbose_name=_("Категорії (фільтри)"),
        help_text=_("У яких категоріях показувати цей атрибут у фільтрах."),
    )
    is_filterable = models.BooleanField(_("У фільтрах"), default=True)
    sort_order = models.PositiveIntegerField(_("Порядок"), default=0)

    class Meta:
        verbose_name = _("Атрибут")
        verbose_name_plural = _("Атрибути")
        ordering = ["sort_order", "name_uk"]

    def __str__(self) -> str:
        return self.name_uk

    @property
    def name(self) -> str:
        return self.localized("name")


class AttributeValue(TimeStampedModel, LocalizedCharMixin):
    attribute = models.ForeignKey(
        Attribute,
        on_delete=models.CASCADE,
        related_name="values",
        verbose_name=_("Атрибут"),
    )
    slug = models.SlugField(_("Slug"), max_length=80)
    name_uk = models.CharField(_("Значення (UK)"), max_length=120)
    name_ru = models.CharField(_("Значення (RU)"), max_length=120, blank=True)
    color_hex = models.CharField(_("Колір HEX"), max_length=7, blank=True)
    sort_order = models.PositiveIntegerField(_("Порядок"), default=0)

    class Meta:
        verbose_name = _("Значення атрибута")
        verbose_name_plural = _("Значення атрибутів")
        ordering = ["sort_order", "name_uk"]
        unique_together = [("attribute", "slug")]

    def __str__(self) -> str:
        return f"{self.attribute.name_uk}: {self.name_uk}"

    @property
    def name(self) -> str:
        return self.localized("name")


class ProductQuerySet(models.QuerySet):
    def published(self):
        return self.filter(is_active=True, status="active")

    def with_price(self):
        return self.annotate(
            min_price=Min(
                "variants__price",
                filter=Q(variants__is_active=True),
            )
        )


class Product(TimeStampedModel, SeoFieldsMixin, LocalizedCharMixin):
    class Status(models.TextChoices):
        ACTIVE = "active", _("Активний")
        INACTIVE = "inactive", _("Неактивний")

    slug = models.SlugField(_("Slug"), max_length=160, unique=True)
    sku = models.CharField(_("Артикул (SKU)"), max_length=64, unique=True)
    barcode = models.CharField(_("Штрихкод"), max_length=64, blank=True)
    price = models.DecimalField(
        _("Ціна"),
        max_digits=10,
        decimal_places=2,
        default=Decimal("0"),
    )
    old_price = models.DecimalField(
        _("Стара ціна"),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    wholesale_price = models.DecimalField(
        _("Оптова ціна"),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    stock = models.PositiveIntegerField(_("Залишок"), default=0)
    name_uk = models.CharField(_("Назва (UK)"), max_length=255)
    name_ru = models.CharField(_("Назва (RU)"), max_length=255, blank=True)
    short_description_uk = models.TextField(_("Короткий опис (UK)"), blank=True)
    short_description_ru = models.TextField(_("Короткий опис (RU)"), blank=True)
    description_uk = models.TextField(_("Опис (UK)"), blank=True)
    description_ru = models.TextField(_("Опис (RU)"), blank=True)
    brand = models.ForeignKey(
        Brand,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
        verbose_name=_("Бренд"),
    )
    primary_category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="primary_products",
        verbose_name=_("Основна категорія"),
    )
    categories = models.ManyToManyField(
        Category,
        blank=True,
        related_name="products",
        verbose_name=_("Категорії"),
    )
    related_products = models.ManyToManyField(
        "self",
        blank=True,
        symmetrical=False,
        related_name="related_from",
        verbose_name=_("Схожі товари"),
    )
    attribute_values = models.ManyToManyField(
        AttributeValue,
        blank=True,
        related_name="products",
        verbose_name=_("Характеристики"),
    )
    availability = models.CharField(
        _("Наявність"),
        max_length=20,
        choices=Availability.choices,
        default=Availability.IN_STOCK,
    )
    status = models.CharField(
        _("Статус"),
        max_length=16,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    is_active = models.BooleanField(_("Активний"), default=True)
    is_hit = models.BooleanField(_("Хіт"), default=False)
    is_new = models.BooleanField(_("Новинка"), default=False)
    is_sale = models.BooleanField(_("Акція"), default=False)
    label_fragrance_free = models.BooleanField(_("Без ароматизаторів"), default=False)
    label_vegan = models.BooleanField(_("Веган-формула"), default=False)
    label_derma_tested = models.BooleanField(_("Дерматологічно протестовано"), default=False)
    label_gentle = models.BooleanField(_("Делікатна формула"), default=False)
    label_hypoallergenic = models.BooleanField(_("Гіпоалергенно"), default=False)
    label_paraben_free = models.BooleanField(_("Без парабенів"), default=False)
    label_cruelty_free = models.BooleanField(_("Без тестів на тваринах"), default=False)
    label_cleansing = models.BooleanField(_("Очищення"), default=False)
    sort_order = models.PositiveIntegerField(_("Порядок"), default=0)
    popularity = models.PositiveIntegerField(_("Популярність"), default=0)
    search_text = models.TextField(_("Пошуковий індекс"), blank=True, editable=False)

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = _("Товар")
        verbose_name_plural = _("Товари")
        ordering = ["sort_order", "-created_at"]

    def __str__(self) -> str:
        return self.name_uk

    @property
    def name(self) -> str:
        return self.localized("name")

    @property
    def short_description(self) -> str:
        return self.localized("short_description")

    @property
    def description(self) -> str:
        return self.localized("description")

    @property
    def labels(self) -> list:
        """Увімкнені чекбоксами мітки — у порядку реєстру PRODUCT_LABELS."""
        return active_labels(self)

    def get_absolute_url(self) -> str:
        return reverse("catalog:product_detail", kwargs={"slug": self.slug})

    def default_variant(self):
        # Не .filter() на related manager — ламає prefetch і дає N+1 у каталозі.
        variants = [v for v in self.variants.all() if v.is_active]
        if not variants:
            return None
        variants.sort(key=lambda v: (v.sort_order, v.pk))
        return variants[0]

    def main_image(self):
        images = list(self.images.all())
        if not images:
            return None
        images.sort(key=lambda img: (not img.is_main, img.sort_order, img.pk))
        return images[0]

    def card_images(self) -> list:
        """До 2 зображень для картки (головне + hover). Використовує prefetch."""
        images = list(self.images.all())
        images.sort(key=lambda img: (not img.is_main, img.sort_order, img.pk))
        return images[:2]

    def hover_image(self):
        images = self.card_images()
        return images[1] if len(images) > 1 else None

    def rebuild_search_text(self) -> str:
        """Single source of truth for the search index."""
        parts = [
            self.name_uk,
            self.name_ru,
            self.short_description_uk,
            self.sku,
            self.barcode,
            self.brand.name_uk if self.brand_id else "",
        ]
        self.search_text = " ".join(p for p in parts if p).casefold()
        return self.search_text

    def sync_commerce_variant(self) -> "ProductVariant":
        """Один прихований ProductVariant для кошика/checkout (джерело правди — поля Product)."""
        variant = (
            self.variants.order_by("sort_order", "pk").first()
            if self.pk
            else None
        )
        created = False
        if variant is None:
            variant = ProductVariant(product=self)
            created = True

        variant.sku = self.sku
        variant.barcode = self.barcode or ""
        variant.price = self.price
        variant.old_price = self.old_price
        variant.wholesale_price = self.wholesale_price
        variant.stock = self.stock
        variant.availability = ""  # успадковувати від товару
        variant.is_active = True
        variant.sort_order = 0
        if not variant.label_uk:
            variant.label_uk = ""
        variant.save()
        return variant

    def save(self, *args, **kwargs) -> None:
        if not (self.sku or "").strip():
            self.sku = f"SKU-{uuid.uuid4().hex[:10].upper()}"
        # status і is_active синхронізуємо: одне джерело правди для вітрини
        self.is_active = self.status == self.Status.ACTIVE
        super().save(*args, **kwargs)
        self.sync_commerce_variant()
        self.rebuild_search_text()
        Product.objects.filter(pk=self.pk).update(search_text=self.search_text)


class ProductVariant(TimeStampedModel):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="variants",
        verbose_name=_("Товар"),
    )
    sku = models.CharField(_("Артикул"), max_length=64, unique=True)
    barcode = models.CharField(_("Штрихкод"), max_length=64, blank=True)
    label_uk = models.CharField(_("Модифікація (UK)"), max_length=120, blank=True)
    label_ru = models.CharField(_("Модифікація (RU)"), max_length=120, blank=True)
    price = models.DecimalField(_("Ціна"), max_digits=10, decimal_places=2)
    old_price = models.DecimalField(
        _("Стара ціна"),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    wholesale_price = models.DecimalField(
        _("Оптова ціна"),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    stock = models.PositiveIntegerField(_("Залишок"), default=0)
    availability = models.CharField(
        _("Наявність (override)"),
        max_length=20,
        choices=Availability.choices,
        blank=True,
        help_text=_("Порожньо = успадкувати від товару"),
    )
    is_active = models.BooleanField(_("Активний"), default=True)
    sort_order = models.PositiveIntegerField(_("Порядок"), default=0)
    attribute_values = models.ManyToManyField(
        AttributeValue,
        blank=True,
        related_name="variants",
        verbose_name=_("Атрибути варіанту"),
    )

    class Meta:
        verbose_name = _("Варіант")
        verbose_name_plural = _("Варіанти")
        ordering = ["sort_order", "id"]

    def __str__(self) -> str:
        return f"{self.product.name_uk} [{self.sku}]"

    @property
    def label(self) -> str:
        from django.utils.translation import get_language

        lang = (get_language() or "uk")[:2]
        if lang == "ru" and self.label_ru:
            return self.label_ru
        return self.label_uk or self.label_ru

    def effective_availability(self) -> str:
        return self.availability or self.product.availability

    def get_effective_availability_display(self) -> str:
        code = self.effective_availability()
        return dict(Availability.choices).get(code, code)

    @property
    def is_purchasable(self) -> bool:
        status = self.effective_availability()
        if status == Availability.OUT_OF_STOCK:
            return False
        if status == Availability.IN_STOCK and self.stock <= 0:
            return False
        return self.is_active and self.product.is_active


class ProductImage(TimeStampedModel):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name=_("Товар"),
    )
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="images",
        verbose_name=_("Варіант"),
    )
    image = OptimizedImageField(
        _("Зображення"),
        upload_to="products/",
        help_text=_(
            "Рекомендовано від 1600px по довгій стороні — інакше збільшення "
            "на сторінці товару може бути розмитим. Менше фото все одно можна зберегти."
        ),
        max_side=MAX_SIDE_PRODUCT,
    )
    alt_uk = models.CharField(_("Назва (UK)"), max_length=255, blank=True)
    alt_ru = models.CharField(_("Назва (RU)"), max_length=255, blank=True)
    is_main = models.BooleanField(_("Головне"), default=False)
    sort_order = models.PositiveIntegerField(_("Порядок"), default=0)

    class Meta:
        verbose_name = _("Зображення товару")
        verbose_name_plural = _("Зображення товарів")
        ordering = ["-is_main", "sort_order", "id"]

    def __str__(self) -> str:
        if self.is_main:
            return "Головне фото"
        if self.pk:
            return f"Фото #{self.pk}"
        return "Нове фото"

    def save(self, *args, **kwargs) -> None:
        super().save(*args, **kwargs)
        if self.is_main and self.product_id:
            (
                ProductImage.objects.filter(product_id=self.product_id)
                .exclude(pk=self.pk)
                .update(is_main=False)
            )


class LabelIcon(models.Model):
    """Заміна PNG-маски мітки товару (ключ = ProductLabel.icon)."""

    key = models.SlugField(_("Ключ іконки"), max_length=64, unique=True)
    title_uk = models.CharField(_("Підпис (UK)"), max_length=120)
    title_ru = models.CharField(_("Підпис (RU)"), max_length=120, blank=True)
    image = OptimizedImageField(
        _("Зображення"),
        upload_to="label_icons/",
        blank=True,
        help_text=_("PNG з прозорим фоном. Порожньо = дефолт із static/img/labels/"),
        max_side=MAX_SIDE_LOGO,
        allow_svg=True,
    )
    updated_at = models.DateTimeField(_("Оновлено"), auto_now=True)

    class Meta:
        verbose_name = _("Іконка мітки")
        verbose_name_plural = _("Іконки міток")
        ordering = ["title_uk"]

    def __str__(self) -> str:
        return self.title_uk

    @property
    def title(self) -> str:
        from django.utils.translation import get_language

        lang = (get_language() or "uk")[:2]
        if lang == "ru" and self.title_ru:
            return self.title_ru
        return self.title_uk

    @classmethod
    def ensure_defaults(cls) -> None:
        from apps.catalog.labels import LABEL_TITLE_RU, PRODUCT_LABELS

        for label in PRODUCT_LABELS:
            title_uk = str(label.title)
            obj, created = cls.objects.get_or_create(
                key=label.icon,
                defaults={
                    "title_uk": title_uk,
                    "title_ru": LABEL_TITLE_RU.get(label.icon, ""),
                },
            )
            if not created and not obj.title_ru:
                ru = LABEL_TITLE_RU.get(label.icon, "")
                if ru:
                    obj.title_ru = ru
                    obj.save(update_fields=["title_ru"])


__all__ = [
    "Attribute",
    "AttributeValue",
    "Availability",
    "Brand",
    "Category",
    "LabelIcon",
    "Product",
    "ProductImage",
    "ProductQuerySet",
    "ProductVariant",
]
