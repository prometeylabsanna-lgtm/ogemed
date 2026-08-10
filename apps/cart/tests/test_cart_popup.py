from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from apps.catalog.models import Availability, Brand, Category, Product, ProductVariant


class CartPopupTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        brand = Brand.objects.create(slug="b", name_uk="Brand")
        cat = Category.objects.create(slug="c", name_uk="Cat")
        cls.product = Product.objects.create(
            slug="p-cart",
            name_uk="Cart Product",
            brand=brand,
            primary_category=cat,
            availability=Availability.IN_STOCK,
            is_active=True,
        )
        cls.variant = ProductVariant.objects.create(
            product=cls.product,
            sku="CART-SKU-1",
            price=Decimal("100.00"),
            old_price=Decimal("150.00"),
            stock=5,
            is_active=True,
        )

    def test_htmx_cart_detail_returns_partial(self):
        response = self.client.get(
            reverse("cart:detail"),
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        body = response.content.decode()
        self.assertNotIn("<html", body.lower())
        self.assertIn("Кошик порожній", body)

    def test_add_from_catalog_updates_count(self):
        response = self.client.post(
            reverse("cart:add"),
            {"variant_id": self.variant.pk, "quantity": 1},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        body = response.content.decode()
        self.assertIn("Cart Product", body)
        self.assertIn('hx-swap-oob="innerHTML:[data-cart-count]"', body)
        self.assertIn("1", body)
        self.assertIn("openCartPopup", response.get("HX-Trigger", ""))

    def test_catalog_card_shows_old_price_and_add(self):
        response = self.client.get(reverse("catalog:list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "До кошика")
        self.assertContains(response, "150")

    def test_cart_qty_input_exposes_stock_max(self):
        self.client.post(
            reverse("cart:add"),
            {"variant_id": self.variant.pk, "quantity": 1},
        )
        response = self.client.get(
            reverse("cart:detail"),
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        body = response.content.decode()
        self.assertIn(f'max="{self.variant.stock}"', body)
        self.assertIn(f'data-stock="{self.variant.stock}"', body)
