from django.contrib import admin
from unfold.admin import ModelAdmin

from apps.core.admin_filters import (
    DropdownFiltersMixin,
    UkAllValuesDropdownFilter,
    UkChoicesDropdownFilter,
)

from .models import PaymentAttempt


@admin.register(PaymentAttempt)
class PaymentAttemptAdmin(DropdownFiltersMixin, ModelAdmin):
    list_display = (
        "order",
        "provider",
        "provider_order_id",
        "status",
        "payment_id",
        "created_at",
    )
    list_filter = (
        ("status", UkChoicesDropdownFilter),
        ("provider", UkAllValuesDropdownFilter),
    )
    search_fields = ("provider_order_id", "payment_id", "order__order_number")
    readonly_fields = ("raw_payload", "created_at", "idempotency_key")
