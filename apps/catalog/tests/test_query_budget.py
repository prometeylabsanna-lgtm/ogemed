"""DB/API probes: N+1 on catalog cards."""
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from apps.catalog.models import Availability, Brand, Category, Product, ProductImage, ProductVariant


class CatalogQueryBudgetTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        brand = Brand.objects.create(slug="qb-brand", name_uk="Brand")
        cat = Category.objects.create(slug="qb-cat", name_uk="Cat")
        for i in range(8):
            product = Product.objects.create(
                slug=f"qb-p-{i}",
                name_uk=f"Product {i}",
                brand=brand,
                primary_category=cat,
                availability=Availability.IN_STOCK,
                is_active=True,
                is_hit=True,
            )
            ProductVariant.objects.create(
                product=product,
                sku=f"QB-SKU-{i}",
                price=Decimal("100.00"),
                old_price=Decimal("120.00"),
                stock=5,
                is_active=True,
            )
            ProductImage.objects.create(
                product=product,
                image=f"products/qb-{i}.jpg",
                is_main=True,
                sort_order=0,
            )
            ProductImage.objects.create(
                product=product,
                image=f"products/qb-{i}-h.jpg",
                is_main=False,
                sort_order=1,
            )

    def test_catalog_list_no_per_product_variant_queries(self):
        # Prefetch variants once; default_variant must not hit DB per card.
        with self.assertNumQueries(15):
            r = self.client.get(reverse("catalog:list"))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Product 0")
        self.assertContains(r, "До кошика")

    def test_default_variant_uses_prefetch(self):
        qs = Product.objects.filter(slug__startswith="qb-p-").prefetch_related(
            "variants"
        )[:3]
        products = list(qs)
        with self.assertNumQueries(0):
            for p in products:
                self.assertIsNotNone(p.default_variant())

    def test_card_images_uses_prefetch(self):
        qs = Product.objects.filter(slug__startswith="qb-p-").prefetch_related(
            "images"
        )[:3]
        products = list(qs)
        with self.assertNumQueries(0):
            for p in products:
                self.assertEqual(len(p.card_images()), 2)
