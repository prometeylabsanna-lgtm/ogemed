from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse
from tinymce.widgets import TinyMCE
from unfold.admin import ModelAdmin

from apps.core.admin_field_hints import AdminFieldHintsMixin
from apps.core.admin_filters import (
    DropdownFiltersMixin,
    UkAllValuesDropdownFilter,
    UkBooleanDropdownFilter,
    UkChoicesDropdownFilter,
)
from apps.core.admin_i18n import LANG_SWITCH_HTML, I18nLangTabsMixin
from apps.core.admin_slug import SlugLockAdminMixin
from apps.core.admin_widgets import IMAGE_FORMFIELD_OVERRIDES

from .about_content import AboutContent
from .info_page_models import InfoPageMeta, InfoPageSection
from .models import CMSPage, Lead


@admin.register(CMSPage)
class CMSPageAdmin(
    SlugLockAdminMixin,
    I18nLangTabsMixin,
    AdminFieldHintsMixin,
    DropdownFiltersMixin,
    ModelAdmin,
):
    list_display = ("title_uk", "slug", "page_key", "is_published", "sort_order")
    list_filter = (
        ("is_published", UkBooleanDropdownFilter),
        ("page_key", UkAllValuesDropdownFilter),
    )
    search_fields = ("title_uk", "title_ru", "slug", "page_key")
    slug_source_field = "title_uk"
    slug_fallback = "page"
    slug_max_length = 120
    fieldsets = (
        (None, {"fields": ("slug", "page_key", "is_published", "sort_order")}),
        (
            "Назва і текст",
            {
                "classes": ("product-i18n-fields",),
                "description": LANG_SWITCH_HTML,
                "fields": ("title_uk", "body_uk", "title_ru", "body_ru"),
            },
        ),
    )

    class Media:
        css = {"all": ("css/admin/slug_lock.css",)}
        js = ("js/admin/slug_lock.js",)

    def has_module_permission(self, request) -> bool:
        return False

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name in ("body_uk", "body_ru"):
            kwargs["widget"] = TinyMCE(attrs={"cols": 80, "rows": 12})
        return super().formfield_for_dbfield(db_field, request, **kwargs)


@admin.register(InfoPageSection)
class InfoPageSectionAdmin(
    I18nLangTabsMixin, AdminFieldHintsMixin, DropdownFiltersMixin, ModelAdmin
):
    list_display = (
        "heading_uk",
        "page_key",
        "layout",
        "sort_order",
        "is_active",
    )
    list_editable = ("sort_order", "is_active")
    list_filter = (
        ("page_key", UkChoicesDropdownFilter),
        ("layout", UkChoicesDropdownFilter),
        ("is_active", UkBooleanDropdownFilter),
    )
    search_fields = ("heading_uk", "heading_ru", "body_uk", "body_ru")
    search_help_text = "Пошук…"
    ordering = ("page_key", "sort_order", "id")
    fieldsets = (
        (
            None,
            {"fields": ("page_key", "layout", "sort_order", "is_active")},
        ),
        (
            "Текст секції",
            {
                "classes": ("product-i18n-fields",),
                "description": LANG_SWITCH_HTML,
                "fields": (
                    "heading_uk",
                    "subheading_uk",
                    "body_uk",
                    "heading_ru",
                    "subheading_ru",
                    "body_ru",
                ),
            },
        ),
    )

    def has_module_permission(self, request) -> bool:
        return False

    @staticmethod
    def _page_key_from_request(request) -> str | None:
        page_key = request.GET.get("page_key__exact") or request.GET.get("page_key")
        if page_key in {c.value for c in InfoPageSection.PageKey}:
            return page_key
        return None

    def get_list_display(self, request):
        if self._page_key_from_request(request):
            return ("heading_uk", "layout", "sort_order", "is_active")
        return self.list_display

    def get_list_filter(self, request):
        if self._page_key_from_request(request):
            return (
                ("layout", UkChoicesDropdownFilter),
                ("is_active", UkBooleanDropdownFilter),
            )
        return self.list_filter

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        page_key = self._page_key_from_request(request)
        if page_key:
            return qs.filter(page_key=page_key)
        return qs

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        page_key = self._page_key_from_request(request)
        if page_key:
            label = dict(InfoPageSection.PageKey.choices)[page_key]
            extra_context["title"] = f"Секції — {label}"
        return super().changelist_view(request, extra_context=extra_context)

    def get_changeform_initial_data(self, request):
        data = super().get_changeform_initial_data(request)
        page_key = self._page_key_from_request(request)
        if page_key:
            data["page_key"] = page_key
        return data

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name in ("body_uk", "body_ru"):
            kwargs["widget"] = TinyMCE(attrs={"cols": 80, "rows": 18})
        return super().formfield_for_dbfield(db_field, request, **kwargs)


@admin.register(InfoPageMeta)
class InfoPageMetaAdmin(
    I18nLangTabsMixin, AdminFieldHintsMixin, DropdownFiltersMixin, ModelAdmin
):
    list_display = ("page_key", "form_title_uk")
    list_filter = (("page_key", UkChoicesDropdownFilter),)
    fieldsets = (
        (None, {"fields": ("page_key",)}),
        (
            "Форма",
            {
                "description": (
                    "Блок форми зворотного звʼязку на інфо-сторінці "
                    "(заголовок, текст і кнопка «Передзвоніть»)."
                    + LANG_SWITCH_HTML
                ),
                "classes": ("product-i18n-fields",),
                "fields": (
                    "cta_title_uk",
                    "cta_text_uk",
                    "cta_title_ru",
                    "cta_text_ru",
                ),
            },
        ),
        (
            "Бічна замітка",
            {
                "classes": ("product-i18n-fields",),
                "fields": (
                    "note_title_uk",
                    "note_steps_uk",
                    "note_text_uk",
                    "note_title_ru",
                    "note_steps_ru",
                    "note_text_ru",
                ),
            },
        ),
    )

    def has_module_permission(self, request) -> bool:
        return False

    @admin.display(description="Заголовок форми", ordering="cta_title_uk")
    def form_title_uk(self, obj):
        return obj.cta_title_uk


@admin.register(AboutContent)
class AboutContentAdmin(I18nLangTabsMixin, AdminFieldHintsMixin, ModelAdmin):
    formfield_overrides = IMAGE_FORMFIELD_OVERRIDES
    fieldsets = (
        (
            "Верхній банер",
            {
                "description": (
                    "Перший великий блок на сторінці «Про нас». "
                    "Якщо фото немає — показується стандартне зображення."
                    + LANG_SWITCH_HTML
                ),
                "classes": ("product-i18n-fields",),
                "fields": (
                    "hero_visible",
                    "hero_image",
                    "hero_kicker_uk",
                    "hero_title_uk",
                    "hero_text_uk",
                    "hero_kicker_ru",
                    "hero_title_ru",
                    "hero_text_ru",
                ),
            },
        ),
        (
            "Історія бренду",
            {
                "classes": ("product-i18n-fields",),
                "fields": (
                    "history_visible",
                    "history_kicker_uk",
                    "history_card_1_title_uk",
                    "history_card_1_body_uk",
                    "history_card_2_title_uk",
                    "history_card_2_body_uk",
                    "history_card_3_title_uk",
                    "history_card_3_body_uk",
                    "history_kicker_ru",
                    "history_card_1_title_ru",
                    "history_card_1_body_ru",
                    "history_card_2_title_ru",
                    "history_card_2_body_ru",
                    "history_card_3_title_ru",
                    "history_card_3_body_ru",
                ),
            },
        ),
        (
            "Філософія догляду",
            {
                "classes": ("product-i18n-fields",),
                "fields": (
                    "philosophy_visible",
                    "philosophy_kicker_uk",
                    "philosophy_title_uk",
                    "philosophy_body_uk",
                    "philosophy_thesis_1_title_uk",
                    "philosophy_thesis_1_text_uk",
                    "philosophy_thesis_2_title_uk",
                    "philosophy_thesis_2_text_uk",
                    "philosophy_thesis_3_title_uk",
                    "philosophy_thesis_3_text_uk",
                    "philosophy_thesis_4_title_uk",
                    "philosophy_thesis_4_text_uk",
                    "philosophy_kicker_ru",
                    "philosophy_title_ru",
                    "philosophy_body_ru",
                    "philosophy_thesis_1_title_ru",
                    "philosophy_thesis_1_text_ru",
                    "philosophy_thesis_2_title_ru",
                    "philosophy_thesis_2_text_ru",
                    "philosophy_thesis_3_title_ru",
                    "philosophy_thesis_3_text_ru",
                    "philosophy_thesis_4_title_ru",
                    "philosophy_thesis_4_text_ru",
                ),
            },
        ),
        (
            "Нижній блок з кнопками",
            {
                "classes": ("product-i18n-fields",),
                "fields": (
                    "cta_visible",
                    "cta_title_uk",
                    "cta_text_uk",
                    "cta_catalog_label_uk",
                    "cta_contacts_label_uk",
                    "cta_title_ru",
                    "cta_text_ru",
                    "cta_catalog_label_ru",
                    "cta_contacts_label_ru",
                ),
            },
        ),
    )

    def has_module_permission(self, request) -> bool:
        return False

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name == "hero_image" and formfield is not None:
            formfield.label = "Зображення банера"
            from apps.core.admin_guidelines import get_image_hint

            formfield.help_text = get_image_hint("about_hero")
        return formfield

    def has_add_permission(self, request) -> bool:
        return not AboutContent.objects.exists()

    def has_delete_permission(self, request, obj=None) -> bool:
        return False

    def changelist_view(self, request, extra_context=None):
        obj = AboutContent.load()
        return HttpResponseRedirect(
            reverse("admin:cms_aboutcontent_change", args=[obj.pk])
        )


@admin.register(Lead)
class LeadAdmin(AdminFieldHintsMixin, DropdownFiltersMixin, ModelAdmin):
    list_display = ("name", "phone", "lead_type", "is_processed", "created_at")
    list_filter = (
        ("lead_type", UkChoicesDropdownFilter),
        ("is_processed", UkBooleanDropdownFilter),
    )
    search_fields = ("name", "phone", "email")
    readonly_fields = ("created_at", "honeypot")


# HeroSlide — лише через CMS «Головна — Hero» (formset), не як окремий ModelAdmin.
from apps.cms import admin_legal_proxies  # noqa: E402, F401
