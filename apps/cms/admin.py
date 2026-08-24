from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse
from unfold.admin import ModelAdmin

from apps.core.admin_filters import (
    DropdownFiltersMixin,
    UkAllValuesDropdownFilter,
    UkBooleanDropdownFilter,
    UkChoicesDropdownFilter,
)

from .about_content import AboutContent
from .models import CMSPage, Lead


@admin.register(CMSPage)
class CMSPageAdmin(DropdownFiltersMixin, ModelAdmin):
    list_display = ("title_uk", "slug", "page_key", "is_published", "sort_order")
    list_filter = (
        ("is_published", UkBooleanDropdownFilter),
        ("page_key", UkAllValuesDropdownFilter),
    )
    search_fields = ("title_uk", "title_ru", "slug", "page_key")
    prepopulated_fields = {"slug": ("title_uk",)}
    fieldsets = (
        (None, {"fields": ("slug", "page_key", "is_published", "sort_order")}),
        ("Українська", {"fields": ("title_uk", "body_uk")}),
        ("Русский", {"fields": ("title_ru", "body_ru")}),
    )


@admin.register(AboutContent)
class AboutContentAdmin(ModelAdmin):
    fieldsets = (
        (
            "Hero",
            {
                "fields": (
                    "hero_visible",
                    "hero_kicker_uk",
                    "hero_kicker_ru",
                    "hero_title_uk",
                    "hero_title_ru",
                    "hero_text_uk",
                    "hero_text_ru",
                    "hero_image",
                ),
            },
        ),
        (
            "Історія бренду",
            {
                "fields": (
                    "history_visible",
                    "history_kicker_uk",
                    "history_kicker_ru",
                    "history_card_1_title_uk",
                    "history_card_1_title_ru",
                    "history_card_1_body_uk",
                    "history_card_1_body_ru",
                    "history_card_2_title_uk",
                    "history_card_2_title_ru",
                    "history_card_2_body_uk",
                    "history_card_2_body_ru",
                    "history_card_3_title_uk",
                    "history_card_3_title_ru",
                    "history_card_3_body_uk",
                    "history_card_3_body_ru",
                ),
            },
        ),
        (
            "Філософія догляду",
            {
                "fields": (
                    "philosophy_visible",
                    "philosophy_kicker_uk",
                    "philosophy_kicker_ru",
                    "philosophy_title_uk",
                    "philosophy_title_ru",
                    "philosophy_body_uk",
                    "philosophy_body_ru",
                    "philosophy_thesis_1_title_uk",
                    "philosophy_thesis_1_title_ru",
                    "philosophy_thesis_1_text_uk",
                    "philosophy_thesis_1_text_ru",
                    "philosophy_thesis_2_title_uk",
                    "philosophy_thesis_2_title_ru",
                    "philosophy_thesis_2_text_uk",
                    "philosophy_thesis_2_text_ru",
                    "philosophy_thesis_3_title_uk",
                    "philosophy_thesis_3_title_ru",
                    "philosophy_thesis_3_text_uk",
                    "philosophy_thesis_3_text_ru",
                    "philosophy_thesis_4_title_uk",
                    "philosophy_thesis_4_title_ru",
                    "philosophy_thesis_4_text_uk",
                    "philosophy_thesis_4_text_ru",
                ),
            },
        ),
        (
            "CTA",
            {
                "fields": (
                    "cta_visible",
                    "cta_title_uk",
                    "cta_title_ru",
                    "cta_text_uk",
                    "cta_text_ru",
                    "cta_catalog_label_uk",
                    "cta_catalog_label_ru",
                    "cta_contacts_label_uk",
                    "cta_contacts_label_ru",
                ),
            },
        ),
    )

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
class LeadAdmin(DropdownFiltersMixin, ModelAdmin):
    list_display = ("name", "phone", "lead_type", "is_processed", "created_at")
    list_filter = (
        ("lead_type", UkChoicesDropdownFilter),
        ("is_processed", UkBooleanDropdownFilter),
    )
    search_fields = ("name", "phone", "email")
    readonly_fields = ("created_at", "honeypot")


# HeroSlide — лише через CMS «Головна — Hero» (formset), не як окремий ModelAdmin.
