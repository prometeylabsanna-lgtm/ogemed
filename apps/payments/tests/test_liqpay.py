import base64
import hashlib
import json
from decimal import Decimal

from django.test import TestCase, override_settings
from django.urls import reverse

from apps.catalog.models import Availability, Brand, Category, Product, ProductVariant
from apps.orders.models import DeliveryType, Order, OrderStatus, PaymentType
from apps.payments.models import PaymentAttempt


class LiqPayCallbackTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        brand = Brand.objects.create(slug="b2", name_uk="B")
        cat = Category.objects.create(slug="c2", name_uk="C")
        product = Product.objects.create(
            slug="p2",
            name_uk="P",
            brand=brand,
            primary_category=cat,
            availability=Availability.IN_STOCK,
            is_active=True,
        )
        ProductVariant.objects.create(
            product=product, sku="SKU-LP", price=Decimal("100.00"), stock=3, is_active=True
        )
        cls.order = Order.objects.create(
            customer_name="Test",
            customer_phone="+380501111111",
            delivery_type=DeliveryType.COURIER,
            payment_type=PaymentType.LIQPAY,
            status=OrderStatus.AWAITING_PAYMENT,
            total=Decimal("100.00"),
            courier_city="Kyiv",
            courier_street="A",
        )

    def _sign(self, private_key: str, data_b64: str) -> str:
        raw = (private_key + data_b64 + private_key).encode()
        return base64.b64encode(hashlib.sha1(raw).digest()).decode()

    @override_settings(LIQPAY_PUBLIC_KEY="pub", LIQPAY_PRIVATE_KEY="priv")
    def test_callback_success_idempotent(self):
        payload = {
            "order_id": self.order.order_number,
            "status": "success",
            "payment_id": "999",
        }
        data_b64 = base64.b64encode(json.dumps(payload).encode()).decode()
        signature = self._sign("priv", data_b64)
        url = reverse("payments:liqpay_callback")
        r1 = self.client.post(url, {"data": data_b64, "signature": signature})
        self.assertEqual(r1.status_code, 200)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, OrderStatus.PROCESSING)
        self.assertEqual(PaymentAttempt.objects.filter(order=self.order).count(), 1)

        r2 = self.client.post(url, {"data": data_b64, "signature": signature})
        self.assertEqual(r2.status_code, 200)
        self.assertEqual(PaymentAttempt.objects.filter(order=self.order).count(), 1)

    @override_settings(LIQPAY_PUBLIC_KEY="pub", LIQPAY_PRIVATE_KEY="priv")
    def test_callback_bad_signature(self):
        payload = {"order_id": self.order.order_number, "status": "success", "payment_id": "1"}
        data_b64 = base64.b64encode(json.dumps(payload).encode()).decode()
        r = self.client.post(
            reverse("payments:liqpay_callback"),
            {"data": data_b64, "signature": "bad"},
        )
        self.assertEqual(r.status_code, 403)
