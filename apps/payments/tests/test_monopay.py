import json
from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.urls import reverse

from apps.catalog.models import Availability, Brand, Category, Product, ProductVariant
from apps.orders.models import DeliveryType, Order, OrderStatus, PaymentType
from apps.payments.models import PaymentAttempt


class MonopayCallbackTests(TestCase):
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
            product=product, sku="SKU-MP", price=Decimal("100.00"), stock=3, is_active=True
        )
        cls.order = Order.objects.create(
            customer_name="Test",
            customer_phone="+380501111111",
            delivery_type=DeliveryType.COURIER,
            payment_type=PaymentType.MONOPAY,
            status=OrderStatus.AWAITING_PAYMENT,
            total=Decimal("100.00"),
            courier_city="Kyiv",
            courier_street="A",
        )

    @override_settings(MONOPAY_TOKEN="test-token")
    @patch("apps.payments.views.MonopayService.verify_webhook", return_value=True)
    def test_callback_success_idempotent(self, _verify):
        payload = {
            "invoiceId": "inv_1",
            "status": "success",
            "reference": self.order.order_number,
            "modifiedDate": "2026-09-28T12:00:00Z",
            "amount": 10000,
            "ccy": 980,
        }
        url = reverse("payments:monopay_callback")
        body = json.dumps(payload)
        r1 = self.client.post(
            url, data=body, content_type="application/json", HTTP_X_SIGN="ok"
        )
        self.assertEqual(r1.status_code, 200)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, OrderStatus.PROCESSING)
        self.assertEqual(PaymentAttempt.objects.filter(order=self.order).count(), 1)

        r2 = self.client.post(
            url, data=body, content_type="application/json", HTTP_X_SIGN="ok"
        )
        self.assertEqual(r2.status_code, 200)
        self.assertEqual(PaymentAttempt.objects.filter(order=self.order).count(), 1)

    @override_settings(MONOPAY_TOKEN="test-token")
    @patch("apps.payments.views.MonopayService.verify_webhook", return_value=False)
    def test_callback_bad_signature(self, _verify):
        payload = {
            "invoiceId": "inv_2",
            "status": "success",
            "reference": self.order.order_number,
            "modifiedDate": "2026-09-28T12:00:01Z",
        }
        r = self.client.post(
            reverse("payments:monopay_callback"),
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_X_SIGN="bad",
        )
        self.assertEqual(r.status_code, 403)
