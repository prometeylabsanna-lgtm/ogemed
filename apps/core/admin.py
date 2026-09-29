from django.contrib import admin
from unfold.admin import ModelAdmin

from apps.core.admin_field_hints import AdminFieldHintsMixin
from apps.core.admin_i18n import LANG_SWITCH_HTML, I18nLangTabsMixin
from apps.core.admin_widgets import IMAGE_FORMFIELD_OVERRIDES
from apps.core.map_embed import normalize_map_embed

from .models import SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(I18nLangTabsMixin, AdminFieldHintsMixin, ModelAdmin):
    formfield_overrides = IMAGE_FORMFIELD_OVERRIDES
    fieldsets = (
        (
            "Контакти",
            {
                "description": (
                    "Карта: вставте посилання на точку Google Maps або код iframe — "
                    "на сайті відобразиться автоматично."
                    + LANG_SWITCH_HTML
                ),
                "classes": ("product-i18n-fields",),
                "fields": (
                    "phone",
                    "phone_2",
                    "email",
                    "manager_email",
                    "address_uk",
                    "work_hours_uk",
                    "address_ru",
                    "work_hours_ru",
                    "map_embed_url",
                ),
            },
        ),
        (
            "Бренд",
            {
                "classes": ("product-i18n-fields",),
                "fields": (
                    "logo",
                    "brand_tagline_uk",
                    "brand_tagline_ru",
                ),
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        if "map_embed_url" in form.cleaned_data:
            obj.map_embed_url = normalize_map_embed(form.cleaned_data["map_embed_url"])
        super().save_model(request, obj, form, change)

    def has_add_permission(self, request) -> bool:
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None) -> bool:
        return False

    def changelist_view(self, request, extra_context=None):
        from django.http import HttpResponseRedirect
        from django.urls import reverse

        obj, _ = SiteSettings.objects.get_or_create(pk=1)
        return HttpResponseRedirect(
            reverse("admin:core_sitesettings_change", args=[obj.pk])
        )


# Proxy CMS sections
from apps.core import admin_site_content_proxies  # noqa: E402, F401
from apps.core import admin_logentry  # noqa: E402, F401
