"""SEO: canonical, noindex, robots, sitemap, seo_* fields."""
from decimal import Decimal

from django.test import TestCase, override_settings
from django.urls import reverse

from apps.catalog.models import Availability, Brand, Category, Product, ProductVariant


@override_settings(SITE_URL="https://ogemed.test")
class SeoMetaTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        brand = Brand.objects.create(
            slug="seo-brand",
            name_uk="SEO Brand",
            seo_title_uk="Brand SEO Title",
            seo_description_uk="Brand SEO desc",
        )
        cat = Category.objects.create(
            slug="seo-cat",
            name_uk="SEO Cat",
            seo_title_uk="Cat SEO Title",
            seo_description_uk="Cat SEO desc",
        )
        cls.product = Product.objects.create(
            slug="seo-product",
            name_uk="SEO Product",
            brand=brand,
            primary_category=cat,
            availability=Availability.IN_STOCK,
            is_active=True,
            seo_title_uk="Custom Product Title",
            seo_description_uk="Custom product description for SEO",
            short_description_uk="Short",
        )
        ProductVariant.objects.create(
            product=cls.product,
            sku="SEO-SKU-1",
            price=Decimal("10.00"),
            stock=3,
            is_active=True,
        )
        cls.brand = brand
        cls.cat = cat

    def test_product_uses_seo_fields_and_canonical(self):
        r = self.client.get(
            reverse("catalog:product_detail", kwargs={"slug": "seo-product"})
        )
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Custom Product Title")
        self.assertContains(r, "Custom product description for SEO")
        self.assertContains(r, 'rel="canonical"')
        self.assertContains(r, "https://ogemed.test/tovar/seo-product/")
        self.assertContains(r, 'hreflang="uk"')
        self.assertContains(r, 'hreflang="ru"')
        self.assertContains(r, 'hreflang="x-default"')

    def test_filtered_catalog_canonical_strips_query(self):
        r = self.client.get(reverse("catalog:list"), {"brand": "seo-brand", "sort": "price_asc"})
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'href="https://ogemed.test/katalog/"')
        self.assertNotContains(r, 'canonical" href="https://ogemed.test/katalog/?')

    def test_cart_is_noindex(self):
        r = self.client.get(reverse("cart:detail"))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'name="robots" content="noindex, nofollow"')

    def test_robots_and_sitemap(self):
        robots = self.client.get("/robots.txt")
        self.assertEqual(robots.status_code, 200)
        self.assertContains(robots, "Disallow: /koshyk/")
        self.assertContains(robots, "Sitemap: https://ogemed.test/sitemap.xml")

        sm = self.client.get("/sitemap.xml")
        self.assertEqual(sm.status_code, 200)
        self.assertContains(sm, "https://ogemed.test/tovar/seo-product/")
        self.assertContains(sm, "https://ogemed.test/katalog/")
