"""Checkout: create Order + OrderItem snapshots from session cart."""
from __future__ import annotations

from decimal import Decimal

from django.db import connection, transaction
from django.db.models import F
from django.utils.translation import gettext as _

from apps.cart.cart import SessionCart
from apps.catalog.models import Availability, ProductVariant

from .models import Order, OrderItem, OrderStatus, PaymentType
from .services_status import OrderStatusService


class InsufficientStockError(Exception):
    """Raised when a cart line can no longer be fulfilled at checkout time."""


@transaction.atomic
def create_order_from_cart(request, cleaned_data: dict) -> Order:
    cart = SessionCart(request)
    lines = cart.lines()
    if not lines:
        raise ValueError("Cart is empty")

    variant_ids = [line.variant.pk for line in lines]
    variants_qs = ProductVariant.objects.select_related("product").filter(pk__in=variant_ids)
    if connection.features.has_select_for_update:
        variants_qs = variants_qs.select_for_update()
    locked_variants = {v.pk: v for v in variants_qs}

    for line in lines:
        variant = locked_variants.get(line.variant.pk)
        if variant is None or not variant.is_purchasable:
            raise InsufficientStockError(
                _("Товар «%(name)s» більше недоступний") % {"name": line.variant.product.name_uk}
            )
        if variant.effective_availability() == Availability.IN_STOCK and variant.stock < line.quantity:
            raise InsufficientStockError(
                _("Недостатньо товару «%(name)s» на складі") % {"name": variant.product.name_uk}
            )

    subtotal = sum((line.line_total for line in lines), Decimal("0"))
    payment_type = cleaned_data["payment_type"]
    if payment_type == PaymentType.LIQPAY:
        initial_status = OrderStatus.AWAITING_PAYMENT
    else:
        initial_status = OrderStatus.PROCESSING

    order = Order(
        user=request.user if request.user.is_authenticated else None,
        customer_name=cleaned_data["customer_name"],
        customer_phone=cleaned_data["customer_phone"],
        customer_email=cleaned_data.get("customer_email", ""),
        delivery_type=cleaned_data["delivery_type"],
        np_city_ref=cleaned_data.get("np_city_ref", ""),
        np_city_name=cleaned_data.get("np_city_name", ""),
        np_warehouse_ref=cleaned_data.get("np_warehouse_ref", ""),
        np_warehouse_name=cleaned_data.get("np_warehouse_name", ""),
        np_point_type=cleaned_data.get("np_point_type", ""),
        courier_city=cleaned_data.get("courier_city", ""),
        courier_street=cleaned_data.get("courier_street", ""),
        courier_building=cleaned_data.get("courier_building", ""),
        courier_apartment=cleaned_data.get("courier_apartment", ""),
        courier_comment=cleaned_data.get("courier_comment", ""),
        payment_type=payment_type,
        subtotal=subtotal,
        total=subtotal,
        status=OrderStatus.NEW,
    )
    order.save()
    # Початковий статус після створення — окремий notify_new_order на checkout.
    OrderStatusService.transition(order, initial_status, notify=False)

    for line in lines:
        variant = locked_variants[line.variant.pk]
        OrderItem.objects.create(
            order=order,
            product=variant.product,
            variant=variant,
            name=variant.product.name_uk,
            sku=variant.sku,
            variant_label=variant.label_uk or variant.label,
            unit_price=variant.price,
            quantity=line.quantity,
            line_total=line.line_total,
        )
        if variant.effective_availability() == Availability.IN_STOCK:
            ProductVariant.objects.filter(pk=variant.pk).update(stock=F("stock") - line.quantity)

    cart.clear()
    request.session["last_order_token"] = order.access_token
    request.session.modified = True
    return order
