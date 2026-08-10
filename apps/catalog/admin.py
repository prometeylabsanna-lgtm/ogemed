from django.contrib import admin

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


class AttributeValueInline(admin.TabularInline):
    model = AttributeValue
    extra = 1


@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ("name_uk", "slug", "is_filterable", "sort_order")
    prepopulated_fields = {"slug": ("name_uk",)}
    inlines = [AttributeValueInline]


@admin.register(AttributeValue)
class AttributeValueAdmin(admin.ModelAdmin):
    list_display = ("name_uk", "attribute", "slug", "sort_order")
    list_filter = ("attribute",)
    prepopulated_fields = {"slug": ("name_uk",)}


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name_uk", "slug", "parent", "is_active", "show_on_home", "sort_order")
    list_filter = ("is_active", "show_on_home")
    list_editable = ("show_on_home", "sort_order")
    search_fields = ("name_uk", "name_ru", "slug")
    prepopulated_fields = {"slug": ("name_uk",)}


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name_uk", "slug", "is_featured", "is_active", "sort_order")
    list_filter = ("is_active", "is_featured", "categories")
    search_fields = ("name_uk", "name_ru", "slug")
    prepopulated_fields = {"slug": ("name_uk",)}
    filter_horizontal = ("categories",)
    fields = (
        "slug",
        "name_uk",
        "name_ru",
        "tagline_uk",
        "tagline_ru",
        "logo",
        "cover_image",
        "showcase_image",
        "categories",
        "is_featured",
        "is_active",
        "sort_order",
        "seo_title",
        "seo_description",
    )


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    form = ProductImageForm
    extra = 1


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = (
        "sku",
        "label_uk",
        "label_ru",
        "price",
        "old_price",
        "stock",
        "availability",
        "is_active",
        "sort_order",
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name_uk",
        "slug",
        "brand",
        "primary_category",
        "availability",
        "is_hit",
        "is_new",
        "is_sale",
        "is_active",
    )
    list_filter = ("is_active", "is_hit", "is_new", "is_sale", "brand", "availability")
    search_fields = ("name_uk", "name_ru", "slug", "search_text")
    prepopulated_fields = {"slug": ("name_uk",)}
    filter_horizontal = ("categories", "attribute_values")
    inlines = [ProductVariantInline, ProductImageInline]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "slug",
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
        ("Українська", {"fields": ("name_uk", "short_description_uk", "description_uk")}),
        ("Русский", {"fields": ("name_ru", "short_description_ru", "description_ru")}),
        ("Характеристики", {"fields": ("attribute_values",)}),
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
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ("sku", "product", "price", "old_price", "stock", "is_active")
    list_filter = ("is_active",)
    search_fields = ("sku", "product__name_uk")
    filter_horizontal = ("attribute_values",)


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    form = ProductImageForm
    list_display = ("product", "variant", "is_main", "sort_order")
    list_filter = ("is_main",)
