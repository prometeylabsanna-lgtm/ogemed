from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from unfold.admin import ModelAdmin, TabularInline

from .models import Order, OrderItem, OrderStatus
from .services_status import OrderStatusService


class OrderItemInline(TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = (
        "name",
        "sku",
        "variant_label",
        "unit_price",
        "quantity",
        "line_total",
        "product",
        "variant",
    )
    can_delete = False


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = (
        "order_number",
        "customer_name",
        "status",
        "payment_type",
        "delivery_type",
        "total",
        "created_at",
    )
    list_filter = ("status", "payment_type", "delivery_type")
    search_fields = ("order_number", "customer_name", "customer_phone", "customer_email")
    readonly_fields = ("order_number", "access_token", "created_at", "updated_at", "subtotal", "total")
    inlines = [OrderItemInline]
    actions = [
        "action_to_processing",
        "action_to_shipped",
        "action_to_done",
        "action_cancel",
    ]

    def _bulk_transition(self, request, queryset, new_status):
        ok = 0
        for order in queryset:
            try:
                OrderStatusService.transition(order, new_status, notify=True)
                ok += 1
            except ValidationError as exc:
                self.message_user(request, f"{order.order_number}: {exc}", messages.ERROR)
        self.message_user(request, f"Оновлено: {ok}", messages.SUCCESS)

    @admin.action(description="→ В обробці")
    def action_to_processing(self, request, queryset):
        self._bulk_transition(request, queryset, OrderStatus.PROCESSING)

    @admin.action(description="→ Відправлено")
    def action_to_shipped(self, request, queryset):
        self._bulk_transition(request, queryset, OrderStatus.SHIPPED)

    @admin.action(description="→ Виконано")
    def action_to_done(self, request, queryset):
        self._bulk_transition(request, queryset, OrderStatus.DONE)

    @admin.action(description="→ Скасовано")
    def action_cancel(self, request, queryset):
        self._bulk_transition(request, queryset, OrderStatus.CANCELLED)

    def save_model(self, request, obj, form, change):
        if change and "status" in form.changed_data:
            new_status = form.cleaned_data["status"]
            previous_status = Order.objects.only("status").get(pk=obj.pk).status
            obj.status = previous_status
            try:
                OrderStatusService.transition(obj, new_status, save=False, notify=True)
            except ValidationError:
                self.message_user(
                    request,
                    _("Заборонений перехід статусу: %(from)s → %(to)s")
                    % {"from": previous_status, "to": new_status},
                    messages.ERROR,
                )
                obj.status = previous_status
        super().save_model(request, obj, form, change)
