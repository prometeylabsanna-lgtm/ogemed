"""Order status machine — all transitions go through this service."""
from __future__ import annotations

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from .models import Order, OrderStatus

ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    OrderStatus.NEW: {
        OrderStatus.AWAITING_PAYMENT,
        OrderStatus.PROCESSING,
        OrderStatus.CANCELLED,
    },
    OrderStatus.AWAITING_PAYMENT: {
        OrderStatus.PAID,
        OrderStatus.CANCELLED,
    },
    OrderStatus.PAID: {
        OrderStatus.PROCESSING,
    },
    OrderStatus.PROCESSING: {
        OrderStatus.SHIPPED,
        OrderStatus.CANCELLED,
    },
    OrderStatus.SHIPPED: {
        OrderStatus.DONE,
    },
    OrderStatus.DONE: set(),
    OrderStatus.CANCELLED: set(),
}


class OrderStatusService:
    @classmethod
    def can_transition(cls, current: str, new: str) -> bool:
        if current == new:
            return True
        return new in ALLOWED_TRANSITIONS.get(current, set())

    @classmethod
    def transition(
        cls,
        order: Order,
        new_status: str,
        *,
        save: bool = True,
        notify: bool = True,
    ) -> Order:
        if not cls.can_transition(order.status, new_status):
            raise ValidationError(
                _("Заборонений перехід статусу: %(from)s → %(to)s")
                % {"from": order.status, "to": new_status}
            )
        previous = order.status
        if previous != new_status:
            order.status = new_status
            if save:
                order.save(update_fields=["status", "updated_at"])
            if notify:
                from apps.notify.services import notify_order_status_changed

                notify_order_status_changed(order, previous_status=previous)
        return order
