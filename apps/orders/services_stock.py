"""Резерв і повернення залишку для позицій замовлення."""
from __future__ import annotations

from django.db import transaction
from django.db.models import F

from apps.catalog.models import Availability, ProductVariant

from .models import Order, OrderItem


def reserve_variant_stock(variant: ProductVariant, quantity: int) -> None:
    """Списати qty з залишку варіанта (те, що перевіряє checkout/кошик)."""
    if quantity <= 0:
        return
    ProductVariant.objects.filter(pk=variant.pk).update(stock=F("stock") - quantity)


def should_reserve_stock(variant: ProductVariant) -> bool:
    return variant.effective_availability() == Availability.IN_STOCK


@transaction.atomic
def release_order_stock(order: Order) -> bool:
    """
    Повернути зарезервований залишок один раз.
    Повертає True, якщо саме зараз повернули; False — якщо вже було / нічого.
    """
    if not order.pk:
        return False

    locked = Order.objects.select_for_update().get(pk=order.pk)
    if locked.stock_restored:
        order.stock_restored = True
        return False

    items = list(
        OrderItem.objects.filter(order_id=locked.pk, stock_reserved=True)
        .exclude(variant_id=None)
        .only("pk", "variant_id", "quantity")
    )
    for item in items:
        qty = item.quantity or 0
        if qty <= 0:
            continue
        ProductVariant.objects.filter(pk=item.variant_id).update(stock=F("stock") + qty)

    locked.stock_restored = True
    locked.save(update_fields=["stock_restored", "updated_at"])
    order.stock_restored = True
    return bool(items)
