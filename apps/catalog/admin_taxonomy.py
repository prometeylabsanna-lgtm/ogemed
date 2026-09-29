"""Адмінка атрибутів, категорій і брендів."""
from django import forms
from django.contrib import admin
from tinymce.widgets import TinyMCE
from unfold.admin import ModelAdmin, TabularInline

from apps.catalog.variant_matrix import COLOR_ATTR_SLUGS
from apps.core.admin_field_hints import AdminFieldHintsMixin
from apps.core.admin_filters import (
    DropdownFiltersMixin,
    UkBooleanDropdownFilter,
    UkRelatedDropdownFilter,
)
from apps.core.admin_i18n import LANG_SWITCH_HTML
from apps.core.admin_slug import SlugLockAdminMixin
from apps.core.admin_widgets import IMAGE_FORMFIELD_OVERRIDES
from apps.core.html_text import TINYMCE_VALID_ELEMENTS

from .models import Attribute, AttributeValue, Brand, Category

RICHTEXT_FIELDS = frozenset({"description_uk", "description_ru"})

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
            "valid_elements": TINYMCE_VALID_ELEMENTS,
            "convert_urls": False,
        },
    )


def _attr_is_color(attribute: Attribute | None) -> bool:
    if attribute is None:
        return False
    slug = (attribute.slug or "").lower()
    if slug in COLOR_ATTR_SLUGS or slug.startswith("kolir") or slug.startswith("color"):
        return True
    name = f"{attribute.name_uk or ''} {attribute.name_ru or ''}".lower()
    return any(token in name for token in ("колір", "цвет", "color", "colour"))


class AttributeValueInlineForm(forms.ModelForm):
    class Meta:
        model = AttributeValue
        fields = ("name_uk", "name_ru", "color_hex", "sort_order")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        parent = getattr(self, "parent_attribute", None)
        if parent is None and self.instance and self.instance.attribute_id:
            parent = self.instance.attribute
        if "color_hex" in self.fields:
            if _attr_is_color(parent):
                self.fields["color_hex"].help_text = (
                    "Код кольору для свотча на сторінці товару, напр. #3D6B4F."
                )
            else:
                self.fields["color_hex"].widget = forms.HiddenInput()
                self.fields["color_hex"].required = False


class AttributeValueInline(TabularInline):
    model = AttributeValue
    form = AttributeValueInlineForm
    extra = 1
    fields = ("name_uk", "name_ru", "color_hex", "sort_order")
    verbose_name = "Значення"
    verbose_name_plural = "Значення атрибута (що обирають у товарі / фільтрі)"

    def get_formset(self, request, obj=None, **kwargs):
        FormSet = super().get_formset(request, obj, **kwargs)
        parent = obj

        class BoundFormSet(FormSet):
            def _construct_form(self, i, **kw):
                form = super()._construct_form(i, **kw)
                form.parent_attribute = parent
                if "color_hex" in form.fields:
                    if _attr_is_color(parent):
                        form.fields["color_hex"].widget = forms.TextInput(
                            attrs=form.fields["color_hex"].widget.attrs
                        )
                        form.fields["color_hex"].help_text = (
                            "HEX для свотча, напр. #3D6B4F. Лише для атрибута кольору."
                        )
                    else:
                        form.fields["color_hex"].widget = forms.HiddenInput()
                return form

        BoundFormSet.__name__ = f"{FormSet.__name__}Bound"
        return BoundFormSet


ATTR_LANG_SWITCH_HTML = (
    '<div class="product-admin-editor__langbar product-admin-editor__langbar--inline" '
    'data-cms-lang-switch role="group" aria-label="Мова контенту">'
    '<button type="button" class="cms-lang-switch__btn is-active" data-cms-lang="uk">UA</button>'
    '<button type="button" class="cms-lang-switch__btn" data-cms-lang="ru">RU</button>'
    '<p class="product-admin-editor__langhint">'
    "Перемикач показує назву українською або російською."
    "</p></div>"
)

ATTR_HELP = (
    "<p>Атрибут — характеристика товарів (тип шкіри, обʼєм, колір…).</p>"
    "<ol style='margin:0.5rem 0 0;padding-left:1.25rem'>"
    "<li>Задайте <strong>назву</strong> (UA/RU).</li>"
    "<li>Нижче додайте <strong>значення</strong> — їх обирають у картці товару "
    "та (якщо увімкнено) у фільтрах каталогу.</li>"
    "<li><strong>Колір HEX</strong> зʼявляється лише для атрибута кольору "
    "(slug <code>kolir</code>) — для кольорових кружечків на PDP.</li>"
    "</ol>"
)


@admin.register(Attribute)
class AttributeAdmin(
    SlugLockAdminMixin, AdminFieldHintsMixin, DropdownFiltersMixin, ModelAdmin
):
    change_form_template = "admin/catalog/i18n_change_form.html"
    slug_fallback = "attr"
    slug_max_length = 80
    list_display = ("name_uk", "slug", "is_filterable", "sort_order")
    list_filter = (("is_filterable", UkBooleanDropdownFilter),)
    inlines = [AttributeValueInline]
    fieldsets = (
        (
            "Загальне",
            {
                "classes": ("product-shared-fields",),
                "description": ATTR_HELP,
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
        css = {
            "all": (
                "css/admin/site_content.css",
                "css/admin/ogemed_theme.css",
                "css/admin/slug_lock.css",
            )
        }
        js = ("js/admin/catalog_lang_tabs.js", "js/admin/slug_lock.js")

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        for name in ("name_uk", "name_ru"):
            if name in form.base_fields:
                form.base_fields[name].label = "Назва"
        return form


def _av_scope(instance, cleaned):
    attr_id = cleaned.get("attribute")
    if hasattr(attr_id, "pk"):
        attr_id = attr_id.pk
    attr_id = attr_id or getattr(instance, "attribute_id", None)
    return {"attribute_id": attr_id} if attr_id else None


@admin.register(AttributeValue)
class AttributeValueAdmin(
    SlugLockAdminMixin, AdminFieldHintsMixin, DropdownFiltersMixin, ModelAdmin
):
    slug_fallback = "value"
    slug_max_length = 80
    slug_scope_from_instance = staticmethod(_av_scope)
    list_display = ("name_uk", "attribute", "slug", "color_hex", "sort_order")
    list_filter = (("attribute", UkRelatedDropdownFilter),)
    fieldsets = (
        (
            None,
            {
                "description": (
                    "Значення атрибута (напр. «Суха», «50 мл»). "
                    "HEX — лише для атрибута кольору."
                ),
                "fields": ("attribute", "slug", "color_hex", "sort_order"),
            },
        ),
        ("Українська", {"fields": ("name_uk",)}),
        ("Русский", {"fields": ("name_ru",)}),
    )

    class Media:
        css = {"all": ("css/admin/slug_lock.css",)}
        js = ("js/admin/slug_lock.js",)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        show_hex = False
        if obj and _attr_is_color(obj.attribute):
            show_hex = True
        attr_id = request.GET.get("attribute")
        if attr_id and not show_hex:
            attr = Attribute.objects.filter(pk=attr_id).first()
            show_hex = _attr_is_color(attr)
        if "color_hex" in form.base_fields and not show_hex:
            form.base_fields["color_hex"].widget = forms.HiddenInput()
            form.base_fields["color_hex"].help_text = ""
        elif "color_hex" in form.base_fields:
            form.base_fields["color_hex"].help_text = (
                "Код кольору для свотча (#RRGGBB). Тільки для атрибута «Колір»."
            )
        return form


@admin.register(Category)
class CategoryAdmin(
    SlugLockAdminMixin, AdminFieldHintsMixin, DropdownFiltersMixin, ModelAdmin
):
    change_form_template = "admin/catalog/i18n_change_form.html"
    formfield_overrides = IMAGE_FORMFIELD_OVERRIDES
    slug_fallback = "category"
    slug_max_length = 120
    list_display = ("category_name", "slug", "parent", "is_active", "sort_order")
    list_display_links = ("category_name",)
    list_filter = (("is_active", UkBooleanDropdownFilter),)
    list_editable = ("sort_order",)
    search_fields = ("name_uk", "name_ru", "slug")
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
        css = {
            "all": (
                "css/admin/site_content.css",
                "css/admin/ogemed_theme.css",
                "css/admin/slug_lock.css",
            )
        }
        js = ("js/admin/catalog_lang_tabs.js", "js/admin/slug_lock.js")

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
class BrandAdmin(
    SlugLockAdminMixin, AdminFieldHintsMixin, DropdownFiltersMixin, ModelAdmin
):
    change_form_template = "admin/catalog/i18n_change_form.html"
    formfield_overrides = IMAGE_FORMFIELD_OVERRIDES
    slug_fallback = "brand"
    slug_max_length = 120
    list_display = ("name_uk", "slug", "is_featured", "is_active", "sort_order")
    list_filter = (
        ("is_active", UkBooleanDropdownFilter),
        ("is_featured", UkBooleanDropdownFilter),
    )
    search_fields = ("name_uk", "name_ru", "slug")
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
        css = {
            "all": (
                "css/admin/site_content.css",
                "css/admin/ogemed_theme.css",
                "css/admin/slug_lock.css",
            )
        }
        js = ("js/admin/catalog_lang_tabs.js", "js/admin/slug_lock.js")

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
