"""Адмінка атрибутів, категорій і брендів."""
from django.contrib import admin
from tinymce.widgets import TinyMCE
from unfold.admin import ModelAdmin, TabularInline

from apps.core.admin_filters import (
    DropdownFiltersMixin,
    UkBooleanDropdownFilter,
    UkRelatedDropdownFilter,
)
from apps.core.admin_widgets import IMAGE_FORMFIELD_OVERRIDES

from .models import Attribute, AttributeValue, Brand, Category

RICHTEXT_FIELDS = frozenset({"description_uk", "description_ru"})

LANG_SWITCH_HTML = (
    '<div class="product-admin-editor__langbar product-admin-editor__langbar--inline" '
    'data-cms-lang-switch role="group" aria-label="Мова контенту">'
    '<button type="button" class="cms-lang-switch__btn is-active" data-cms-lang="uk">UA</button>'
    '<button type="button" class="cms-lang-switch__btn" data-cms-lang="ru">RU</button>'
    '<p class="product-admin-editor__langhint">'
    "Перемикач показує назву, описи та SEO українською або російською."
    "</p></div>"
)

LABEL_LANG_SWITCH_HTML = (
    '<div class="product-admin-editor__langbar product-admin-editor__langbar--inline" '
    'data-cms-lang-switch role="group" aria-label="Мова контенту">'
    '<button type="button" class="cms-lang-switch__btn is-active" data-cms-lang="uk">UA</button>'
    '<button type="button" class="cms-lang-switch__btn" data-cms-lang="ru">RU</button>'
    '<p class="product-admin-editor__langhint">'
    "Перемикач показує підпис іконки українською або російською."
    "</p></div>"
)


def tinymce_widget():
    return TinyMCE(
        attrs={"cols": 80, "rows": 14},
        mce_attrs={
            "height": 360,
            "menubar": False,
            "plugins": "lists link code",
            "toolbar": (
                "undo redo | bold italic underline | forecolor fontsize | "
                "bullist numlist | link | code"
            ),
            "font_size_formats": "12px 14px 16px 18px 20px 24px 28px 32px",
        },
    )


class AttributeValueInline(TabularInline):
    model = AttributeValue
    extra = 1


ATTR_LANG_SWITCH_HTML = (
    '<div class="product-admin-editor__langbar product-admin-editor__langbar--inline" '
    'data-cms-lang-switch role="group" aria-label="Мова контенту">'
    '<button type="button" class="cms-lang-switch__btn is-active" data-cms-lang="uk">UA</button>'
    '<button type="button" class="cms-lang-switch__btn" data-cms-lang="ru">RU</button>'
    '<p class="product-admin-editor__langhint">'
    "Перемикач показує назву українською або російською. "
    "Таблиця значень атрибутів нижче не змінюється."
    "</p></div>"
)


@admin.register(Attribute)
class AttributeAdmin(DropdownFiltersMixin, ModelAdmin):
    change_form_template = "admin/catalog/i18n_change_form.html"
    list_display = ("name_uk", "slug", "is_filterable", "sort_order")
    list_filter = (("is_filterable", UkBooleanDropdownFilter),)
    prepopulated_fields = {"slug": ("name_uk",)}
    inlines = [AttributeValueInline]
    fieldsets = (
        (
            "Загальне",
            {
                "classes": ("product-shared-fields",),
                "fields": ("slug", "is_filterable", "sort_order"),
            },
        ),
        (
            "Назва",
            {
                "classes": ("product-i18n-fields",),
                "description": ATTR_LANG_SWITCH_HTML,
                "fields": ("name_uk", "name_ru"),
            },
        ),
    )

    class Media:
        css = {"all": ("css/admin/site_content.css", "css/admin/ogemed_theme.css")}
        js = ("js/admin/catalog_lang_tabs.js",)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        for name in ("name_uk", "name_ru"):
            if name in form.base_fields:
                form.base_fields[name].label = "Назва"
        return form


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
    change_form_template = "admin/catalog/i18n_change_form.html"
    formfield_overrides = IMAGE_FORMFIELD_OVERRIDES
    list_display = ("category_name", "slug", "parent", "is_active", "sort_order")
    list_display_links = ("category_name",)
    list_filter = (("is_active", UkBooleanDropdownFilter),)
    list_editable = ("sort_order",)
    search_fields = ("name_uk", "name_ru", "slug")
    prepopulated_fields = {"slug": ("name_uk",)}
    fieldsets = (
        (
            None,
            {
                "classes": ("product-shared-fields",),
                "fields": (
                    "parent",
                    "slug",
                    "image",
                    "is_active",
                    "sort_order",
                ),
            },
        ),
        (
            "Назва, опис і SEO",
            {
                "classes": ("product-i18n-fields",),
                "description": LANG_SWITCH_HTML,
                "fields": (
                    "name_uk",
                    "description_uk",
                    "seo_title_uk",
                    "seo_description_uk",
                    "name_ru",
                    "description_ru",
                    "seo_title_ru",
                    "seo_description_ru",
                ),
            },
        ),
    )

    class Media:
        css = {"all": ("css/admin/site_content.css", "css/admin/ogemed_theme.css")}
        js = ("js/admin/catalog_lang_tabs.js",)

    @admin.display(description="Назва", ordering="name_uk")
    def category_name(self, obj: Category):
        return obj.name_uk

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        for name, label in (
            ("name_uk", "Назва"),
            ("name_ru", "Назва"),
            ("description_uk", "Опис"),
            ("description_ru", "Опис"),
            ("seo_title_uk", "SEO title"),
            ("seo_title_ru", "SEO title"),
            ("seo_description_uk", "SEO description"),
            ("seo_description_ru", "SEO description"),
        ):
            if name in form.base_fields:
                form.base_fields[name].label = label
        return form

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name in RICHTEXT_FIELDS:
            kwargs["widget"] = tinymce_widget()
        return super().formfield_for_dbfield(db_field, request, **kwargs)


@admin.register(Brand)
class BrandAdmin(DropdownFiltersMixin, ModelAdmin):
    change_form_template = "admin/catalog/i18n_change_form.html"
    formfield_overrides = IMAGE_FORMFIELD_OVERRIDES
    list_display = ("name_uk", "slug", "is_featured", "is_active", "sort_order")
    list_filter = (
        ("is_active", UkBooleanDropdownFilter),
        ("is_featured", UkBooleanDropdownFilter),
    )
    search_fields = ("name_uk", "name_ru", "slug")
    prepopulated_fields = {"slug": ("name_uk",)}
    fieldsets = (
        (
            None,
            {
                "classes": ("product-shared-fields",),
                "fields": (
                    "slug",
                    "cover_image",
                    "showcase_image",
                    "is_featured",
                    "is_active",
                    "sort_order",
                ),
            },
        ),
        (
            "Назва, опис і SEO",
            {
                "classes": ("product-i18n-fields",),
                "description": LANG_SWITCH_HTML,
                "fields": (
                    "name_uk",
                    "tagline_uk",
                    "description_uk",
                    "seo_title_uk",
                    "seo_description_uk",
                    "name_ru",
                    "tagline_ru",
                    "description_ru",
                    "seo_title_ru",
                    "seo_description_ru",
                ),
            },
        ),
    )

    class Media:
        css = {"all": ("css/admin/site_content.css", "css/admin/ogemed_theme.css")}
        js = ("js/admin/catalog_lang_tabs.js",)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        for name, label in (
            ("name_uk", "Назва"),
            ("name_ru", "Назва"),
            ("tagline_uk", "Короткий опис"),
            ("tagline_ru", "Короткий опис"),
            ("description_uk", "Опис / історія"),
            ("description_ru", "Опис / історія"),
            ("seo_title_uk", "SEO title"),
            ("seo_title_ru", "SEO title"),
            ("seo_description_uk", "SEO description"),
            ("seo_description_ru", "SEO description"),
        ):
            if name in form.base_fields:
                form.base_fields[name].label = label
        return form

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name in RICHTEXT_FIELDS:
            kwargs["widget"] = tinymce_widget()
        return super().formfield_for_dbfield(db_field, request, **kwargs)
