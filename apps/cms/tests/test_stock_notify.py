from decimal import Decimal
from unittest.mock import patch

from django.test import Client, TestCase
from django.urls import reverse

from apps.catalog.models import Availability, Brand, Category, Product, ProductVariant
from apps.cms.models import Lead


class StockNotifyLeadTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.brand = Brand.objects.create(slug="b", name_uk="B")
        cls.cat = Category.objects.create(slug="c", name_uk="C")
        cls.product = Product.objects.create(
            slug="serum-out",
            name_uk="Сироватка out",
            brand=cls.brand,
            primary_category=cls.cat,
            availability=Availability.OUT_OF_STOCK,
            is_active=True,
        )
        cls.variant = ProductVariant.objects.create(
            product=cls.product,
            sku="OUT-001",
            label_uk="30 мл",
            price=Decimal("100.00"),
            stock=0,
            is_active=True,
        )

    def setUp(self):
        self.client = Client()

    def test_catalog_card_shows_stock_notify(self):
        r = self.client.get(reverse("catalog:list"))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Повідомити про надходження")
        self.assertContains(r, 'data-stock-notify-trigger')
        self.assertNotContains(r, f'value="{self.variant.pk}"')

    def test_pdp_shows_stock_notify(self):
        r = self.client.get(
            reverse("catalog:product_detail", kwargs={"slug": "serum-out"})
        )
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Повідомити про надходження")
        self.assertContains(r, 'data-stock-notify-trigger')

    @patch("apps.cms.lead_views.notify_new_lead")
    def test_stock_notify_lead_creates_with_phone(self, notify):
        r = self.client.post(
            reverse("cms:lead_create"),
            {
                "lead_type": Lead.LeadType.STOCK_NOTIFY,
                "phone": "+380501112233",
                "product_label": "Сироватка out — 30 мл",
                "product_url": "/tovar/serum-out/",
                "website": "",
            },
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Дякуємо")
        lead = Lead.objects.get()
        self.assertEqual(lead.lead_type, Lead.LeadType.STOCK_NOTIFY)
        self.assertEqual(lead.phone, "+380501112233")
        self.assertIn("Сироватка out", lead.message)
        self.assertEqual(lead.name, "Клієнт")
        notify.assert_called_once()

    def test_on_order_keeps_add_to_cart(self):
        self.product.availability = Availability.ON_ORDER
        self.product.save(update_fields=["availability"])
        r = self.client.get(reverse("catalog:list"))
        self.assertContains(r, "До кошика")
        self.assertNotContains(r, 'data-stock-notify-trigger')
        self.assertNotContains(r, 'data-price-inquiry-trigger')
