"""Regression probes for critical e-commerce invariants."""
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from apps.catalog.models import Availability, Brand, Category, Product, ProductVariant
from apps.orders.models import DeliveryType, Order, PaymentType


def _variant(*, sku: str, stock: int) -> ProductVariant:
    brand = Brand.objects.create(slug=f"b-{sku.lower()}", name_uk="Brand")
    cat = Category.objects.create(slug=f"c-{sku.lower()}", name_uk="Cat")
    product = Product.objects.create(
        slug=f"p-{sku.lower()}",
        name_uk="Product",
        brand=brand,
        primary_category=cat,
        availability=Availability.IN_STOCK,
        is_active=True,
    )
    return ProductVariant.objects.create(
        product=product,
        sku=sku,
        price=Decimal("100.00"),
        stock=stock,
        is_active=True,
    )


class CartStockGuardTests(TestCase):
    def test_add_rejects_qty_above_stock(self):
        """Кошик не повинен приймати qty > stock для IN_STOCK."""
        variant = _variant(sku="CRIT-OV-1", stock=2)
        r = self.client.post(
            reverse("cart:add"),
            {"variant_id": variant.pk, "quantity": 50},
        )
        self.assertEqual(r.status_code, 400)
        self.assertEqual(self.client.session.get("cart") or {}, {})

    def test_add_caps_or_rejects_when_cart_plus_qty_exceeds_stock(self):
        variant = _variant(sku="CRIT-OV-2", stock=3)
        ok = self.client.post(
            reverse("cart:add"),
            {"variant_id": variant.pk, "quantity": 2},
        )
        self.assertEqual(ok.status_code, 302)
        over = self.client.post(
            reverse("cart:add"),
            {"variant_id": variant.pk, "quantity": 2},
        )
        self.assertEqual(over.status_code, 400)
        cart = self.client.session.get("cart") or {}
        self.assertEqual(int(cart[str(variant.pk)]), 2)

    def test_set_qty_rejects_above_stock(self):
        variant = _variant(sku="CRIT-OV-3", stock=2)
        self.client.post(reverse("cart:add"), {"variant_id": variant.pk, "quantity": 1})
        r = self.client.post(
            reverse("cart:update"),
            {"variant_id": variant.pk, "quantity": 9},
        )
        self.assertEqual(r.status_code, 400)
        cart = self.client.session.get("cart") or {}
        self.assertEqual(int(cart[str(variant.pk)]), 1)


class CheckoutIdempotencyHints(TestCase):
    def test_second_submit_after_success_does_not_duplicate(self):
        variant = _variant(sku="CRIT-IDEM-1", stock=5)
        self.client.post(reverse("cart:add"), {"variant_id": variant.pk, "quantity": 1})
        payload = {
            "customer_name": "Ідемпотент",
            "customer_phone": "+380501112233",
            "delivery_type": DeliveryType.COURIER,
            "courier_city": "Київ",
            "courier_street": "Тест",
            "payment_type": PaymentType.CASH_ON_DELIVERY,
        }
        first = self.client.post(reverse("orders:checkout"), payload)
        second = self.client.post(reverse("orders:checkout"), payload)
        self.assertEqual(first.status_code, 302)
        self.assertEqual(second.status_code, 302)
        self.assertEqual(Order.objects.filter(customer_name="Ідемпотент").count(), 1)
