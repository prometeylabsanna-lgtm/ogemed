from django.db import models
from django.db.models import Min, Q
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

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
    image = models.ImageField(_("Зображення"), upload_to="categories/", blank=True)
    description_uk = models.TextField(_("Опис (UK)"), blank=True)
    description_ru = models.TextField(_("Опис (RU)"), blank=True)
    is_active = models.BooleanField(_("Активна"), default=True)
    show_on_home = models.BooleanField(
        _("Швидкі категорії на головній"),
        default=False,
        help_text=_("Якщо увімкнено — категорія зʼявиться в блоці на головній."),
    )
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
    logo = models.ImageField(_("Логотип"), upload_to="brands/", blank=True)
    logo_dark = models.ImageField(
        _("Логотип (темний)"),
        upload_to="brands/",
        blank=True,
        help_text=_("Варіант для темного фону."),
    )
    website_url = models.URLField(_("Сайт бренду"), blank=True)
    description_uk = models.TextField(_("Опис / історія (UK)"), blank=True)
    description_ru = models.TextField(_("Опис / історія (RU)"), blank=True)
    cover_image = models.ImageField(
        _("Фото для каталогу"),
        upload_to="brands/covers/",
        blank=True,
        help_text=_("Плитка бренду у фільтрах каталогу."),
    )
    showcase_image = models.ImageField(
        _("Зображення для вітрини на головній"),
        upload_to="brands/showcase/",
        blank=True,
        help_text=_("PNG без фону. Якщо порожнє — візьметься фото для каталогу."),
    )
    categories = models.ManyToManyField(
        "catalog.Category",
        blank=True,
        related_name="brands",
        verbose_name=_("Категорії"),
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
        DRAFT = "draft", _("Чернетка")
        ARCHIVED = "archived", _("Архів")

    slug = models.SlugField(_("Slug"), max_length=160, unique=True)
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
        """Single source of truth for the search index (also used by the
        ProductVariant post_save signal — keep both in sync via this method).
        """
        skus = " ".join(self.variants.values_list("sku", flat=True))
        parts = [
            self.name_uk,
            self.name_ru,
            self.short_description_uk,
            skus,
            self.brand.name_uk if self.brand_id else "",
        ]
        self.search_text = " ".join(p for p in parts if p).casefold()
        return self.search_text

    def save(self, *args, **kwargs) -> None:
        super().save(*args, **kwargs)
        # Rebuild after save (self.pk is guaranteed) so it always includes
        # existing variant SKUs instead of overwriting them with a stale value.
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
    image = models.ImageField(
        _("Зображення"),
        upload_to="products/",
        help_text=_("Від 1600px по довгій стороні — фото збільшується на сторінці товару."),
    )
    alt_uk = models.CharField(_("Alt (UK)"), max_length=255, blank=True)
    alt_ru = models.CharField(_("Alt (RU)"), max_length=255, blank=True)
    is_main = models.BooleanField(_("Головне"), default=False)
    sort_order = models.PositiveIntegerField(_("Порядок"), default=0)

    class Meta:
        verbose_name = _("Зображення товару")
        verbose_name_plural = _("Зображення товарів")
        ordering = ["-is_main", "sort_order", "id"]

    def __str__(self) -> str:
        return f"Image #{self.pk} for {self.product_id}"


__all__ = [
    "Attribute",
    "AttributeValue",
    "Availability",
    "Brand",
    "Category",
    "Product",
    "ProductImage",
    "ProductQuerySet",
    "ProductVariant",
]
