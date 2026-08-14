from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import Client, TestCase
from django.urls import reverse

from apps.catalog.models import Availability, Brand, Category, Product, ProductVariant
from apps.orders.models import (
    DeliveryType,
    Order,
    OrderStatus,
    PaymentType,
)
from apps.orders.services_status import OrderStatusService


class CartCheckoutTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        brand = Brand.objects.create(slug="b", name_uk="Brand")
        cat = Category.objects.create(slug="c", name_uk="Cat")
        cls.product = Product.objects.create(
            slug="p1",
            name_uk="Product 1",
            brand=brand,
            primary_category=cat,
            availability=Availability.IN_STOCK,
            is_active=True,
        )
        cls.variant = ProductVariant.objects.create(
            product=cls.product,
            sku="SKU-1",
            price=Decimal("250.00"),
            stock=10,
            is_active=True,
        )

    def test_add_to_cart_and_totals(self):
        r = self.client.post(reverse("cart:add"), {"variant_id": self.variant.pk, "quantity": 2})
        self.assertEqual(r.status_code, 302)
        r = self.client.get(reverse("cart:detail"))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Product 1")
        self.assertContains(r, "500")

    def test_checkout_creates_order_cod(self):
        self.client.post(reverse("cart:add"), {"variant_id": self.variant.pk, "quantity": 1})
        r = self.client.post(
            reverse("orders:checkout"),
            {
                "customer_name": "Іван Тест",
                "customer_phone": "+380501112233",
                "customer_email": "ivan@example.com",
                "delivery_type": DeliveryType.COURIER,
                "courier_city": "Київ",
                "courier_street": "Хрещатик",
                "courier_building": "1",
                "payment_type": PaymentType.CASH_ON_DELIVERY,
            },
        )
        self.assertEqual(r.status_code, 302)
        order = Order.objects.get()
        self.assertEqual(order.status, OrderStatus.PROCESSING)
        self.assertEqual(order.items.count(), 1)
        item = order.items.first()
        self.assertEqual(item.sku, "SKU-1")
        self.assertEqual(item.unit_price, Decimal("250.00"))
        self.assertEqual(item.name, "Product 1")

    def test_thank_you_access_control(self):
        self.client.post(reverse("cart:add"), {"variant_id": self.variant.pk})
        self.client.post(
            reverse("orders:checkout"),
            {
                "customer_name": "Іван",
                "customer_phone": "+380501112233",
                "delivery_type": DeliveryType.COURIER,
                "courier_city": "Київ",
                "courier_street": "А",
                "payment_type": PaymentType.CASH_ON_DELIVERY,
            },
        )
        order = Order.objects.get()
        ok = self.client.get(
            reverse("orders:thank_you"),
            {"order": order.order_number, "t": order.access_token},
        )
        self.assertEqual(ok.status_code, 200)
        self.assertContains(ok, order.order_number)

        other = Client()
        denied = other.get(
            reverse("orders:thank_you"),
            {"order": order.order_number},
        )
        self.assertEqual(denied.status_code, 404)

    def test_status_transitions(self):
        order = Order.objects.create(
            customer_name="A",
            customer_phone="1",
            delivery_type=DeliveryType.COURIER,
            payment_type=PaymentType.CASH_ON_DELIVERY,
            status=OrderStatus.NEW,
        )
        OrderStatusService.transition(order, OrderStatus.PROCESSING)
        self.assertEqual(order.status, OrderStatus.PROCESSING)
        with self.assertRaises(ValidationError):
            OrderStatusService.transition(order, OrderStatus.PAID)

    def test_liqpay_checkout_awaits_payment(self):
        self.client.post(reverse("cart:add"), {"variant_id": self.variant.pk})
        self.client.post(
            reverse("orders:checkout"),
            {
                "customer_name": "Іван",
                "customer_phone": "+380501112233",
                "delivery_type": DeliveryType.NOVA_POSHTA,
                "np_city_name": "Київ",
                "np_warehouse_name": "Відділення 1",
                "np_point_type": "warehouse",
                "payment_type": PaymentType.LIQPAY,
            },
        )
        order = Order.objects.get()
        self.assertEqual(order.status, OrderStatus.AWAITING_PAYMENT)

    def test_fop_checkout_awaits_payment_and_shows_requisites(self):
        from apps.core.models import SiteSettings

        site = SiteSettings.load()
        site.fop_recipient_name = "ФОП Тестова"
        site.fop_iban = "UA123456789012345678901234567"
        site.fop_card_number = "5168755511112222"
        site.fop_edrpou = "1234567890"
        site.save()

        self.client.post(reverse("cart:add"), {"variant_id": self.variant.pk})
        r = self.client.post(
            reverse("orders:checkout"),
            {
                "customer_name": "Іван",
                "customer_phone": "+380501112233",
                "delivery_type": DeliveryType.COURIER,
                "courier_city": "Київ",
                "courier_street": "Хрещатик",
                "payment_type": PaymentType.FOP_CARD,
            },
        )
        self.assertEqual(r.status_code, 302)
        order = Order.objects.get()
        self.assertEqual(order.payment_type, PaymentType.FOP_CARD)
        self.assertEqual(order.status, OrderStatus.AWAITING_PAYMENT)

        thank = self.client.get(
            reverse("orders:thank_you"),
            {"order": order.order_number, "t": order.access_token},
        )
        self.assertEqual(thank.status_code, 200)
        self.assertContains(thank, "ФОП Тестова")
        self.assertContains(thank, "UA123456789012345678901234567")
        self.assertContains(thank, f"Оплата замовлення №{order.order_number}")
        self.assertContains(thank, "Скопіювати реквізити")

    def test_checkout_page_lists_fop_payment(self):
        self.client.post(reverse("cart:add"), {"variant_id": self.variant.pk})
        r = self.client.get(reverse("orders:checkout"))
        self.assertContains(r, "fop_card")
        self.assertContains(r, "Оплата на картку / рахунок ФОП")
        self.assertContains(r, "ви отримаєте реквізити")

    def test_checkout_rejects_invalid_phone(self):
        self.client.post(reverse("cart:add"), {"variant_id": self.variant.pk})
        r = self.client.post(
            reverse("orders:checkout"),
            {
                "customer_name": "Іван",
                "customer_phone": "12345",
                "delivery_type": DeliveryType.COURIER,
                "courier_city": "Київ",
                "courier_street": "Хрещатик",
                "payment_type": PaymentType.CASH_ON_DELIVERY,
            },
        )
        self.assertEqual(r.status_code, 400)
        self.assertEqual(Order.objects.count(), 0)
        self.assertContains(r, "телефон", status_code=400)
