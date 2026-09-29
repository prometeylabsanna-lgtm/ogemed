from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from apps.catalog.models import Availability, Brand, Category, Product, ProductVariant
from apps.orders.models import DeliveryType, Order, OrderStatus, PaymentType
from apps.orders.services_status import OrderStatusService
from apps.orders.services_stock import release_order_stock


class StockReserveReleaseTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        brand = Brand.objects.create(slug="stock-b", name_uk="Brand")
        cat = Category.objects.create(slug="stock-c", name_uk="Cat")
        cls.product = Product.objects.create(
            slug="stock-p",
            name_uk="Stock Product",
            brand=brand,
            primary_category=cat,
            availability=Availability.IN_STOCK,
            price=Decimal("100.00"),
            stock=10,
            sku="STOCK-SKU-1",
            is_active=True,
            status=Product.Status.ACTIVE,
        )
        cls.variant = cls.product.variants.get()

    def _checkout(self, qty: int = 2):
        self.client.post(
            reverse("cart:add"),
            {"variant_id": self.variant.pk, "quantity": qty},
        )
        r = self.client.post(
            reverse("orders:checkout"),
            {
                "customer_name": "Тест",
                "customer_phone": "+380501112233",
                "delivery_type": DeliveryType.COURIER,
                "courier_city": "Київ",
                "courier_street": "Хрещатик",
                "courier_building": "1",
                "payment_type": PaymentType.CASH_ON_DELIVERY,
            },
        )
        self.assertEqual(r.status_code, 302)
        return Order.objects.get()

    def test_checkout_reserves_stock(self):
        order = self._checkout(qty=3)
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock, 7)
        item = order.items.get()
        self.assertTrue(item.stock_reserved)
        self.assertFalse(order.stock_restored)

    def test_cancel_restores_stock_once(self):
        order = self._checkout(qty=2)
        OrderStatusService.transition(order, OrderStatus.CANCELLED, notify=False)
        self.variant.refresh_from_db()
        order.refresh_from_db()
        self.assertEqual(order.status, OrderStatus.CANCELLED)
        self.assertTrue(order.stock_restored)
        self.assertEqual(self.variant.stock, 10)

        # повторне «повернення» не подвоює
        release_order_stock(order)
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock, 10)

    def test_on_order_does_not_reserve(self):
        self.product.availability = Availability.ON_ORDER
        self.product.stock = 5
        self.product.save()
        self.variant.refresh_from_db()

        order = self._checkout(qty=2)
        self.variant.refresh_from_db()
        item = order.items.get()
        self.assertFalse(item.stock_reserved)
        self.assertEqual(self.variant.stock, 5)

        OrderStatusService.transition(order, OrderStatus.CANCELLED, notify=False)
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock, 5)
