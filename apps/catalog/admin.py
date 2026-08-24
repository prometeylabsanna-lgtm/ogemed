from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin, TabularInline

from apps.core.admin_filters import (
    DropdownFiltersMixin,
    UkBooleanDropdownFilter,
    UkChoicesDropdownFilter,
    UkRelatedDropdownFilter,
)
from apps.core.image_processing import thumb_url

from .forms import ProductImageForm
from .labels import LABEL_FIELDS, LABELS_BY_FIELD, label_icon_url
from .models import (
    Attribute,
    AttributeValue,
    Brand,
    Category,
    LabelIcon,
    Product,
    ProductImage,
    ProductVariant,
)


class AttributeValueInline(TabularInline):
    model = AttributeValue
    extra = 1


@admin.register(Attribute)
class AttributeAdmin(DropdownFiltersMixin, ModelAdmin):
    list_display = ("name_uk", "slug", "is_filterable", "sort_order")
    list_filter = (("is_filterable", UkBooleanDropdownFilter),)
    prepopulated_fields = {"slug": ("name_uk",)}
    filter_horizontal = ("categories",)
    inlines = [AttributeValueInline]
    fieldsets = (
        (None, {"fields": ("slug", "is_filterable", "sort_order", "categories")}),
        ("Українська", {"fields": ("name_uk",)}),
        ("Русский", {"fields": ("name_ru",)}),
    )


@admin.register(AttributeValue)
class AttributeValueAdmin(DropdownFiltersMixin, ModelAdmin):
    list_display = ("name_uk", "attribute", "slug", "color_hex", "sort_order")
    list_filter = (("attribute", UkRelatedDropdownFilter),)
    prepopulated_fields = {"slug": ("name_uk",)}
    fieldsets = (
        (None, {"fields": ("attribute", "slug", "color_hex", "sort_order")}),
        ("Українська", {"fields": ("name_uk",)}),
        ("Русский", {"fields": ("name_ru",)}),
    )


@admin.register(Category)
class CategoryAdmin(DropdownFiltersMixin, ModelAdmin):
    list_display = ("name_uk", "slug", "parent", "is_active", "show_on_home", "sort_order")
    list_filter = (
        ("is_active", UkBooleanDropdownFilter),
        ("show_on_home", UkBooleanDropdownFilter),
    )
    list_editable = ("show_on_home", "sort_order")
    search_fields = ("name_uk", "name_ru", "slug")
    prepopulated_fields = {"slug": ("name_uk",)}
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "parent",
                    "slug",
                    "image",
                    "is_active",
                    "show_on_home",
                    "sort_order",
                )
            },
        ),
        ("Українська", {"fields": ("name_uk", "description_uk")}),
        ("Русский", {"fields": ("name_ru", "description_ru")}),
        ("SEO", {"fields": ("seo_title", "seo_description"), "classes": ("collapse",)}),
    )


@admin.register(Brand)
class BrandAdmin(DropdownFiltersMixin, ModelAdmin):
    list_display = ("name_uk", "slug", "is_featured", "is_active", "sort_order")
    list_filter = (
        ("is_active", UkBooleanDropdownFilter),
        ("is_featured", UkBooleanDropdownFilter),
        ("categories", UkRelatedDropdownFilter),
    )
    search_fields = ("name_uk", "name_ru", "slug")
    prepopulated_fields = {"slug": ("name_uk",)}
    filter_horizontal = ("categories",)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "slug",
                    "website_url",
                    "logo",
                    "logo_dark",
                    "cover_image",
                    "showcase_image",
                    "categories",
                    "is_featured",
                    "is_active",
                    "sort_order",
                )
            },
        ),
        (
            "Українська",
            {"fields": ("name_uk", "tagline_uk", "description_uk")},
        ),
        (
            "Русский",
            {"fields": ("name_ru", "tagline_ru", "description_ru")},
        ),
        ("SEO", {"fields": ("seo_title", "seo_description"), "classes": ("collapse",)}),
    )


class ProductImageInline(TabularInline):
    model = ProductImage
    form = ProductImageForm
    extra = 1
    readonly_fields = ("preview",)
    fields = ("preview", "image", "variant", "alt_uk", "alt_ru", "is_main", "sort_order")

    @admin.display(description="Превʼю")
    def preview(self, obj: ProductImage):
        if not obj.pk or not obj.image:
            return "—"
        return format_html(
            '<img src="{}" alt="" width="56" height="56" '
            'style="object-fit:cover;border-radius:4px">',
            thumb_url(obj.image),
        )


class ProductVariantInline(TabularInline):
    model = ProductVariant
    extra = 1
    fields = (
        "sku",
        "barcode",
        "label_uk",
        "label_ru",
        "price",
        "old_price",
        "wholesale_price",
        "stock",
        "availability",
        "is_active",
        "sort_order",
    )


@admin.register(Product)
class ProductAdmin(DropdownFiltersMixin, ModelAdmin):
    list_display = (
        "name_uk",
        "slug",
        "brand",
        "primary_category",
        "status",
        "availability",
        "is_hit",
        "is_new",
        "is_sale",
        "is_active",
    )
    list_filter = (
        ("status", UkChoicesDropdownFilter),
        ("availability", UkChoicesDropdownFilter),
        ("brand", UkRelatedDropdownFilter),
        ("is_active", UkBooleanDropdownFilter),
        ("is_hit", UkBooleanDropdownFilter),
        ("is_new", UkBooleanDropdownFilter),
        ("is_sale", UkBooleanDropdownFilter),
    )
    search_fields = ("name_uk", "name_ru", "slug", "search_text")
    prepopulated_fields = {"slug": ("name_uk",)}
    filter_horizontal = ("categories", "attribute_values", "related_products")
    inlines = [ProductVariantInline, ProductImageInline]
    fieldsets = (
        (
            "Загальне",
            {
                "fields": (
                    "slug",
                    "status",
                    "brand",
                    "primary_category",
                    "categories",
                    "availability",
                    "is_active",
                    "is_hit",
                    "is_new",
                    "is_sale",
                    "sort_order",
                    "popularity",
                )
            },
        ),
        (
            "Українська",
            {"fields": ("name_uk", "short_description_uk", "description_uk")},
        ),
        (
            "Русский",
            {"fields": ("name_ru", "short_description_ru", "description_ru")},
        ),
        (
            "Звʼязки",
            {"fields": ("attribute_values", "related_products")},
        ),
        (
            "Мітки (іконки в картці товару)",
            {
                "fields": LABEL_FIELDS,
                "description": (
                    "Позначені мітки виводяться рядком під описом товару. "
                    "Превʼю іконки — під кожним перемикачем. "
                    "Заміна файлів: розділ «Іконки міток» у меню."
                ),
            },
        ),
        ("SEO", {"fields": ("seo_title", "seo_description"), "classes": ("collapse",)}),
    )

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        label = LABELS_BY_FIELD.get(db_field.name)
        if label and formfield is not None:
            url = label_icon_url(label.icon)
            formfield.help_text = format_html(
                '<img src="{}" alt="{}" class="admin-label-icon-preview" width="40" height="40">',
                url,
                label.title,
            )
        return formfield


@admin.register(LabelIcon)
class LabelIconAdmin(ModelAdmin):
    list_display = ("preview", "title", "key", "updated_at")
    readonly_fields = ("key", "title", "preview_large", "updated_at")
    fields = ("title", "key", "preview_large", "image", "updated_at")
    ordering = ("title",)

    @admin.display(description="Превʼю")
    def preview(self, obj: LabelIcon):
        url = thumb_url(obj.image) if obj.image else label_icon_url(obj.key)
        return format_html(
            '<img src="{}" alt="{}" class="admin-label-icon-preview" width="40" height="40">',
            url,
            obj.title,
        )

    @admin.display(description="Поточна іконка")
    def preview_large(self, obj: LabelIcon):
        url = thumb_url(obj.image) if obj.image else label_icon_url(obj.key)
        return format_html(
            '<img src="{}" alt="{}" class="admin-label-icon-preview--lg" width="72" height="72">',
            url,
            obj.title,
        )

    def has_add_permission(self, request) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return False

    def changelist_view(self, request, extra_context=None):
        LabelIcon.ensure_defaults()
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(ProductVariant)
class ProductVariantAdmin(DropdownFiltersMixin, ModelAdmin):
    list_display = (
        "sku",
        "barcode",
        "product",
        "price",
        "wholesale_price",
        "old_price",
        "stock",
        "is_active",
    )
    list_filter = (("is_active", UkBooleanDropdownFilter),)
    search_fields = ("sku", "barcode", "product__name_uk")
    filter_horizontal = ("attribute_values",)

    def has_module_permission(self, request) -> bool:
        # Приховано з меню / app list — редагування лише inline у товарі
        return False


@admin.register(ProductImage)
class ProductImageAdmin(DropdownFiltersMixin, ModelAdmin):
    form = ProductImageForm
    list_display = ("preview", "product", "variant", "is_main", "sort_order")
    list_filter = (("is_main", UkBooleanDropdownFilter),)
    search_fields = ("product__name_uk", "alt_uk")

    @admin.display(description="Превʼю")
    def preview(self, obj: ProductImage):
        if not obj.image:
            return "—"
        return format_html(
            '<img src="{}" alt="" width="48" height="48" '
            'style="object-fit:cover;border-radius:4px">',
            thumb_url(obj.image),
        )
