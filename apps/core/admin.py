from django.contrib import admin

from .models import SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            "Контакти",
            {
                "fields": (
                    "phone",
                    "email",
                    "manager_email",
                    "address_uk",
                    "address_ru",
                    "work_hours_uk",
                    "work_hours_ru",
                    "map_embed_url",
                ),
            },
        ),
        (
            "Соцмережі / месенджери",
            {
                "fields": (
                    "telegram_url",
                    "instagram_url",
                    "facebook_url",
                    "viber_url",
                    "telegram_consultant_url",
                ),
            },
        ),
        (
            "Бренд",
            {
                "fields": (
                    "logo",
                    "brand_tagline_uk",
                    "brand_tagline_ru",
                ),
            },
        ),
        (
            "Реквізити ФОП (оплата на картку / IBAN)",
            {
                "fields": (
                    "fop_recipient_name",
                    "fop_iban",
                    "fop_card_number",
                    "fop_edrpou",
                ),
            },
        ),
    )

    def has_add_permission(self, request) -> bool:
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None) -> bool:
        return False
