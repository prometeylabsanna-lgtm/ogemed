from django.contrib import admin
from django.contrib.admin.actions import delete_selected
from django.utils.html import format_html
from unfold.admin import ModelAdmin, TabularInline

from apps.core.admin_field_hints import AdminFieldHintsMixin
from apps.core.admin_filters import (
    DropdownFiltersMixin,
    UkBooleanDropdownFilter,
    UkChoicesDropdownFilter,
    UkRelatedDropdownFilter,
)
from apps.core.admin_slug import SlugLockAdminMixin
from apps.core.admin_widgets import IMAGE_FORMFIELD_OVERRIDES
from apps.core.image_processing import thumb_url

from .admin_product_actions import PRODUCT_ADMIN_ACTIONS
from .admin_product_filters import PRODUCT_ATTRIBUTE_ADMIN_FILTERS
from .admin_product_form import ProductAdminForm, attribute_select_field_names
from .admin_taxonomy import (
    LABEL_LANG_SWITCH_HTML,
    LANG_SWITCH_HTML,
    RICHTEXT_FIELDS,
    tinymce_widget,
)
from .forms import ProductImageForm
from .labels import LABEL_FIELDS, LABELS_BY_FIELD, label_icon_url
from .models import LabelIcon, Product, ProductImage, ProductVariant

# Реєстрація Attribute / Category / Brand
from . import admin_taxonomy  # noqa: F401


class ProductImageInline(TabularInline):
    model = ProductImage
    form = ProductImageForm
    formfield_overrides = IMAGE_FORMFIELD_OVERRIDES
    extra = 1
    fields = ("image", "alt_uk", "alt_ru", "is_main")
    ordering = ("-is_main", "id")


@admin.register(Product)
class ProductAdmin(
    SlugLockAdminMixin, AdminFieldHintsMixin, DropdownFiltersMixin, ModelAdmin
):
    change_form_template = "admin/catalog/product/change_form.html"
    form = ProductAdminForm
    formfield_overrides = IMAGE_FORMFIELD_OVERRIDES
    slug_fallback = "product"
    slug_max_length = 160
    list_display = (
        "name_uk",
        "sku",
        "price",
        "stock",
        "brand",
        "status",
        "availability",
    )
    list_filter = (
        ("status", UkChoicesDropdownFilter),
        ("availability", UkChoicesDropdownFilter),
        ("brand", UkRelatedDropdownFilter),
        ("is_hit", UkBooleanDropdownFilter),
        ("is_new", UkBooleanDropdownFilter),
        ("is_sale", UkBooleanDropdownFilter),
        *PRODUCT_ATTRIBUTE_ADMIN_FILTERS,
    )
    actions = (*PRODUCT_ADMIN_ACTIONS, delete_selected)
    search_fields = ("name_uk", "name_ru", "slug", "sku", "barcode", "search_text")
    filter_horizontal = ("related_products",)
    inlines = [ProductImageInline]
    fieldsets = (
        (
            "Артикул і ціна",
            {
                "classes": ("product-shared-fields",),
                "fields": (
                    "sku",
                    "barcode",
                    "price",
                    "old_price",
                    "wholesale_price",
                    "stock",
                    "availability",
                ),
                "description": (
                    "Один артикул на товар. Ціна й залишок зʼявляються на сайті "
                    "та в кошику автоматично."
                ),
            },
        ),
        (
            "Загальне",
            {
                "classes": ("product-shared-fields",),
                "fields": (
                    "slug",
                    "status",
                    "brand",
                    "primary_category",
                    "is_hit",
                    "is_new",
                    "is_sale",
                ),
                "description": (
                    "Основна категорія визначає розділ товару в каталозі. "
                    "Додаткові категорії на формі не потрібні."
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
                    "short_description_uk",
                    "description_uk",
                    "seo_title_uk",
                    "seo_description_uk",
                    "name_ru",
                    "short_description_ru",
                    "description_ru",
                    "seo_title_ru",
                    "seo_description_ru",
                ),
            },
        ),
        (
            "Звʼязки",
            {
                "classes": ("product-shared-fields",),
                "fields": ("related_products",),
            },
        ),
        (
            "Мітки на сторінці товару",
            {
                "classes": ("labels-grid", "product-shared-fields"),
                "fields": LABEL_FIELDS,
                "description": (
                    "Увімкнені мітки показуються <strong>іконками під описом</strong> "
                    "на сторінці товару (PDP). Заміна малюнків — меню "
                    "«Каталог → Іконки міток»."
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
        js = (
            "js/admin/catalog_lang_tabs.js",
            "js/admin/product_image_main.js",
            "js/admin/slug_lock.js",
        )

    def get_fieldsets(self, request, obj=None):
        fieldsets = list(super().get_fieldsets(request, obj))
        attr_fields = attribute_select_field_names()
        insert_at = next(
            (i for i, (title, _) in enumerate(fieldsets) if title == "Звʼязки"),
            len(fieldsets),
        )
        fieldsets.insert(
            insert_at,
            (
                "Характеристики",
                {
                    "classes": ("product-attrs-grid", "product-shared-fields"),
                    "fields": attr_fields,
                    "description": (
                        "Для кожної характеристики оберіть одне значення "
                        "у випадаючому списку. Порожньо = не показувати."
                    ),
                },
            ),
        )
        return fieldsets

    def get_form(self, request, obj=None, **kwargs):
        fields = kwargs.get("fields")
        if fields is not None:
            kwargs["fields"] = tuple(
                f for f in fields if not str(f).startswith("attr_select_")
            )
        form = super().get_form(request, obj, **kwargs)
        label_map = {
            "name_uk": "Назва",
            "name_ru": "Назва",
            "short_description_uk": "Короткий опис",
            "short_description_ru": "Короткий опис",
            "description_uk": "Опис",
            "description_ru": "Опис",
            "seo_title_uk": "SEO title",
            "seo_title_ru": "SEO title",
            "seo_description_uk": "SEO description",
            "seo_description_ru": "SEO description",
        }
        for name, label in label_map.items():
            if name in form.base_fields:
                form.base_fields[name].label = label
        return form

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name in RICHTEXT_FIELDS:
            kwargs["widget"] = tinymce_widget()
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        label = LABELS_BY_FIELD.get(db_field.name)
        if label and formfield is not None:
            url = label_icon_url(label.icon)
            formfield.help_text = format_html(
                '<img src="{}" alt="{}" class="admin-label-icon-preview" width="40" height="40">',
                url,
                label.display_title(),
            )
        return formfield

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        formfield = super().formfield_for_manytomany(db_field, request, **kwargs)
        if db_field.name == "related_products" and formfield is not None:
            formfield.help_text = ""
        return formfield

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        if hasattr(form, "save_attribute_values"):
            form.save_attribute_values()
        obj = form.instance
        if not obj.pk:
            return
        if obj.primary_category_id:
            obj.categories.set([obj.primary_category_id])
        else:
            obj.categories.clear()


@admin.register(LabelIcon)
class LabelIconAdmin(AdminFieldHintsMixin, ModelAdmin):
    change_form_template = "admin/catalog/i18n_change_form.html"
    formfield_overrides = IMAGE_FORMFIELD_OVERRIDES
    list_display = ("preview", "title_uk", "title_ru", "key", "updated_at")
    readonly_fields = ("key", "preview_large", "updated_at")
    fieldsets = (
        (
            "Загальне",
            {
                "classes": ("product-shared-fields",),
                "fields": ("key", "preview_large", "image", "updated_at"),
            },
        ),
        (
            "Підпис",
            {
                "classes": ("product-i18n-fields",),
                "description": LABEL_LANG_SWITCH_HTML,
                "fields": ("title_uk", "title_ru"),
            },
        ),
    )
    ordering = ("title_uk",)

    class Media:
        css = {"all": ("css/admin/site_content.css", "css/admin/ogemed_theme.css")}
        js = ("js/admin/catalog_lang_tabs.js",)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        for name in ("title_uk", "title_ru"):
            if name in form.base_fields:
                form.base_fields[name].label = "Підпис"
        return form

    @admin.display(description="Превʼю")
    def preview(self, obj: LabelIcon):
        url = thumb_url(obj.image) if obj.image else label_icon_url(obj.key)
        return format_html(
            '<img src="{}" alt="{}" class="admin-label-icon-preview" width="40" height="40">',
            url,
            obj.title_uk,
        )

    @admin.display(description="Поточна іконка")
    def preview_large(self, obj: LabelIcon):
        url = thumb_url(obj.image) if obj.image else label_icon_url(obj.key)
        return format_html(
            '<img src="{}" alt="{}" class="admin-label-icon-preview--lg" width="72" height="72">',
            url,
            obj.title_uk,
        )

    def has_add_permission(self, request) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return False

    def changelist_view(self, request, extra_context=None):
        LabelIcon.ensure_defaults()
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(ProductVariant)
class ProductVariantAdmin(AdminFieldHintsMixin, DropdownFiltersMixin, ModelAdmin):
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
        return False


@admin.register(ProductImage)
class ProductImageAdmin(AdminFieldHintsMixin, DropdownFiltersMixin, ModelAdmin):
    form = ProductImageForm
    formfield_overrides = IMAGE_FORMFIELD_OVERRIDES
    list_display = ("product", "variant", "is_main", "sort_order")
    list_filter = (("is_main", UkBooleanDropdownFilter),)
    fields = ("product", "variant", "image", "alt_uk", "alt_ru", "is_main")

    class Media:
        js = ("js/admin/product_image_main.js",)
