from decimal import Decimal
from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from PIL import Image

from apps.catalog.models import (
    Attribute,
    AttributeValue,
    Availability,
    Brand,
    Category,
    Product,
    ProductImage,
    ProductVariant,
)
from apps.catalog.services import apply_catalog_filters, has_active_filters, published_products


def _make_image(name="t.jpg"):
    buf = BytesIO()
    Image.new("RGB", (8, 8), color=(200, 100, 50)).save(buf, format="JPEG")
    return SimpleUploadedFile(name, buf.getvalue(), content_type="image/jpeg")


class CatalogStorefrontTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.brand = Brand.objects.create(slug="ogemed", name_uk="OGEMED", name_ru="OGEMED")
        cls.cat = Category.objects.create(slug="oblychchya", name_uk="Обличчя", name_ru="Лицо")
        cls.product = Product.objects.create(
            slug="serum-test",
            name_uk="Сироватка тест",
            name_ru="Сыворотка тест",
            brand=cls.brand,
            primary_category=cls.cat,
            availability=Availability.IN_STOCK,
            is_active=True,
            is_hit=True,
            is_new=True,
            sku="TEST-SKU-001",
            price=Decimal("100.00"),
            stock=5,
        )
        cls.product.categories.add(cls.cat)
        cls.variant = cls.product.variants.get(sku="TEST-SKU-001")
        cls.variant.label_uk = "30 мл"
        cls.variant.save(update_fields=["label_uk"])
        cls.variant_b = ProductVariant.objects.create(
            product=cls.product,
            sku="TEST-SKU-002",
            label_uk="50 мл",
            price=Decimal("140.00"),
            stock=3,
            is_active=True,
        )
        cls.img_shared = ProductImage.objects.create(
            product=cls.product,
            image=_make_image("shared.jpg"),
            is_main=True,
            sort_order=0,
        )
        cls.img_a = ProductImage.objects.create(
            product=cls.product,
            variant=cls.variant,
            image=_make_image("a.jpg"),
            sort_order=1,
        )
        cls.img_b = ProductImage.objects.create(
            product=cls.product,
            variant=cls.variant_b,
            image=_make_image("b.jpg"),
            sort_order=1,
        )

    def test_catalog_list(self):
        r = self.client.get(reverse("catalog:list"))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Сироватка тест")
        self.assertContains(r, 'class="breadcrumbs"')

    def test_category_page(self):
        r = self.client.get(reverse("catalog:category", kwargs={"slug": "oblychchya"}))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Обличчя")

    def test_pdp(self):
        r = self.client.get(reverse("catalog:product_detail", kwargs={"slug": "serum-test"}))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "TEST-SKU-001")
        self.assertContains(r, "100")
        self.assertContains(r, "data-pdp-gallery")

    def test_variant_htmx_swaps_gallery_oob(self):
        url = reverse("catalog:product_detail", kwargs={"slug": "serum-test"})
        r = self.client.get(
            url,
            {"variant": self.variant_b.pk, "partial": "variant"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(r.status_code, 200)
        body = r.content.decode()
        self.assertIn("TEST-SKU-002", body)
        self.assertIn('id="pdp-gallery"', body)
        self.assertIn("hx-swap-oob", body)
        self.assertIn(self.img_b.image.url, body)
        self.assertNotIn(self.img_a.image.url, body)

    def test_search_by_name(self):
        r = self.client.get(reverse("catalog:search"), {"q": "Сироватка"})
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Сироватка тест")

    def test_search_by_sku(self):
        r = self.client.get(reverse("catalog:search"), {"q": "TEST-SKU-001"})
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Сироватка тест")

    def test_search_suggest_json(self):
        r = self.client.get(reverse("catalog:search_suggest"), {"q": "Сиро"})
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(data["q"], "Сиро")
        self.assertTrue(data["results"])
        self.assertEqual(data["results"][0]["name"], "Сироватка тест")
        self.assertIn("/tovar/", data["results"][0]["url"])

    def test_search_suggest_short_query(self):
        r = self.client.get(reverse("catalog:search_suggest"), {"q": "С"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["results"], [])

    def test_search_empty(self):
        r = self.client.get(reverse("catalog:search"), {"q": "zzzz-none"})
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Нічого не знайдено")

    def test_home_has_hits(self):
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Сироватка тест")
        self.assertNotContains(r, 'class="breadcrumbs"')

    def test_home_care_selection_cta(self):
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'class="care-selection-section')
        self.assertContains(r, "Знайдіть свій ідеальний догляд")
        self.assertContains(r, 'href="/katalog/"')
        self.assertContains(r, 'href="/katalog/?skin_type=select"')

    def test_catalog_alias_redirect_keeps_skin_type(self):
        r = self.client.get("/catalog/", {"skin_type": "select"})
        self.assertEqual(r.status_code, 302)
        self.assertIn("/katalog/", r["Location"])
        self.assertIn("skin_type=select", r["Location"])

    def test_skin_type_select_opens_filter_context(self):
        r = self.client.get(reverse("catalog:list"), {"skin_type": "select"})
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.context["skin_type_select"])
        self.assertEqual(r.context["selected_skin_type"], "")
        self.assertFalse(r.context["has_active_filters"])

    def test_skin_type_filter_matches_attribute(self):
        attr = Attribute.objects.create(
            slug="typ-shkiry",
            name_uk="Тип шкіри",
            name_ru="Тип кожи",
            is_filterable=True,
        )
        dry = AttributeValue.objects.create(
            attribute=attr,
            slug="sukha",
            name_uk="Суха",
            name_ru="Сухая",
        )
        other = AttributeValue.objects.create(
            attribute=attr,
            slug="normalna",
            name_uk="Нормальна",
            name_ru="Нормальная",
        )
        self.product.attribute_values.set([dry])

        other_product = Product.objects.create(
            slug="cream-test",
            name_uk="Крем тест",
            name_ru="Крем тест",
            brand=self.brand,
            primary_category=self.cat,
            availability=Availability.IN_STOCK,
            is_active=True,
        )
        other_product.attribute_values.set([other])
        ProductVariant.objects.create(
            product=other_product,
            sku="CREAM-001",
            label_uk="50 мл",
            price=Decimal("80.00"),
            stock=2,
            is_active=True,
        )

        qs = apply_catalog_filters(published_products(), {"skin_type": "sukha"})
        self.assertEqual(list(qs.values_list("slug", flat=True)), ["serum-test"])
        self.assertTrue(has_active_filters({"skin_type": "sukha"}))
        self.assertFalse(has_active_filters({"skin_type": "select"}))

        r = self.client.get(reverse("catalog:list"), {"skin_type": "sukha"})
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Сироватка тест")
        self.assertNotContains(r, "Крем тест")

    def test_application_filter_matches_attribute(self):
        attr = Attribute.objects.create(
            slug="zastosuvannya",
            name_uk="Застосування",
            name_ru="Применение",
            is_filterable=True,
        )
        home = AttributeValue.objects.create(
            attribute=attr,
            slug="dlya-domashnogo-doglyadu",
            name_uk="Для домашнього догляду",
            name_ru="Для домашнего ухода",
        )
        pro = AttributeValue.objects.create(
            attribute=attr,
            slug="dlya-kosmetologiv",
            name_uk="Для косметологів",
            name_ru="Для косметологов",
        )
        self.product.attribute_values.set([home])

        other_product = Product.objects.create(
            slug="pro-product",
            name_uk="Проф товар",
            name_ru="Проф товар",
            brand=self.brand,
            primary_category=self.cat,
            availability=Availability.IN_STOCK,
            is_active=True,
        )
        other_product.attribute_values.set([pro])
        ProductVariant.objects.create(
            product=other_product,
            sku="PRO-001",
            label_uk="10 мл",
            price=Decimal("90.00"),
            stock=2,
            is_active=True,
        )

        qs = apply_catalog_filters(
            published_products(), {"application": "dlya-domashnogo-doglyadu"}
        )
        self.assertEqual(list(qs.values_list("slug", flat=True)), ["serum-test"])
        self.assertTrue(
            has_active_filters({"application": "dlya-domashnogo-doglyadu"})
        )

        r = self.client.get(
            reverse("catalog:list"),
            {"application": "dlya-domashnogo-doglyadu"},
        )
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Сироватка тест")
        self.assertNotContains(r, "Проф товар")
        self.assertContains(r, 'name="application"')

    def test_availability_filter_and_stock_on_card(self):
        other = Product.objects.create(
            slug="serum-order",
            name_uk="Сироватка під замовлення",
            name_ru="Сыворотка под заказ",
            brand=self.brand,
            primary_category=self.cat,
            availability=Availability.ON_ORDER,
            is_active=True,
        )
        ProductVariant.objects.create(
            product=other,
            sku="ORDER-001",
            label_uk="30 мл",
            price=Decimal("120.00"),
            stock=0,
            is_active=True,
        )

        qs = apply_catalog_filters(
            published_products(), {"availability": Availability.IN_STOCK}
        )
        self.assertEqual(list(qs.values_list("slug", flat=True)), ["serum-test"])
        self.assertTrue(has_active_filters({"availability": "in_stock"}))

        r = self.client.get(
            reverse("catalog:list"), {"availability": Availability.IN_STOCK}
        )
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Сироватка тест")
        self.assertContains(r, "В наявності")
        self.assertContains(r, "5 шт")
        self.assertNotContains(r, "Сироватка під замовлення")
        self.assertContains(r, 'name="availability"')

    def test_catalog_load_more_partial(self):
        r = self.client.get(
            reverse("catalog:list"),
            {"page": 1, "more": "1"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Сироватка тест")
        self.assertContains(r, 'id="catalog-more"')

    def test_variant_product_relation(self):
        self.assertEqual(self.variant.product_id, self.product.pk)
        self.assertEqual(self.product.default_variant().sku, "TEST-SKU-001")
