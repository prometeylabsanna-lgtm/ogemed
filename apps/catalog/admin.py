from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from .forms import ProductImageForm
from .labels import LABEL_FIELDS
from .models import (
    Attribute,
    AttributeValue,
    Brand,
    Category,
    Product,
    ProductImage,
    ProductVariant,
)


class AttributeValueInline(TabularInline):
    model = AttributeValue
    extra = 1


@admin.register(Attribute)
class AttributeAdmin(ModelAdmin):
    list_display = ("name_uk", "slug", "is_filterable", "sort_order")
    prepopulated_fields = {"slug": ("name_uk",)}
    filter_horizontal = ("categories",)
    inlines = [AttributeValueInline]
    fieldsets = (
        (None, {"fields": ("slug", "is_filterable", "sort_order", "categories")}),
        ("Українська", {"fields": ("name_uk",)}),
        ("Русский", {"fields": ("name_ru",)}),
    )


@admin.register(AttributeValue)
class AttributeValueAdmin(ModelAdmin):
    list_display = ("name_uk", "attribute", "slug", "color_hex", "sort_order")
    list_filter = ("attribute",)
    prepopulated_fields = {"slug": ("name_uk",)}
    fieldsets = (
        (None, {"fields": ("attribute", "slug", "color_hex", "sort_order")}),
        ("Українська", {"fields": ("name_uk",)}),
        ("Русский", {"fields": ("name_ru",)}),
    )


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ("name_uk", "slug", "parent", "is_active", "show_on_home", "sort_order")
    list_filter = ("is_active", "show_on_home")
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
class BrandAdmin(ModelAdmin):
    list_display = ("name_uk", "slug", "is_featured", "is_active", "sort_order")
    list_filter = ("is_active", "is_featured", "categories")
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
    fields = ("image", "alt_uk", "alt_ru", "variant", "is_main", "sort_order")


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
class ProductAdmin(ModelAdmin):
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
        "status",
        "is_active",
        "is_hit",
        "is_new",
        "is_sale",
        "brand",
        "availability",
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
                "description": "Позначені мітки виводяться рядком під описом товару.",
            },
        ),
        ("SEO", {"fields": ("seo_title", "seo_description"), "classes": ("collapse",)}),
    )


@admin.register(ProductVariant)
class ProductVariantAdmin(ModelAdmin):
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
    list_filter = ("is_active",)
    search_fields = ("sku", "barcode", "product__name_uk")
    filter_horizontal = ("attribute_values",)


@admin.register(ProductImage)
class ProductImageAdmin(ModelAdmin):
    form = ProductImageForm
    list_display = ("product", "variant", "is_main", "sort_order")
    list_filter = ("is_main",)
