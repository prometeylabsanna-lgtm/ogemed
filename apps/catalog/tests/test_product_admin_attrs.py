"""Адмінка товару: характеристики як select-и."""
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from apps.catalog.admin_product_form import ATTR_FIELD_PREFIX, ProductAdminForm
from apps.catalog.models import Attribute, AttributeValue, Product


class ProductAdminAttrsTests(TestCase):
    def setUp(self):
        self.attr = Attribute.objects.create(
            slug="volume",
            name_uk="Обʼєм",
            is_filterable=True,
            sort_order=1,
        )
        self.v30 = AttributeValue.objects.create(
            attribute=self.attr,
            slug="30-ml",
            name_uk="30 мл",
            sort_order=1,
        )
        self.v50 = AttributeValue.objects.create(
            attribute=self.attr,
            slug="50-ml",
            name_uk="50 мл",
            sort_order=2,
        )
        self.product = Product.objects.create(
            slug="test-attrs",
            sku="ATTR-1",
            name_uk="Тест атрибутів",
            price=100,
        )
        self.product.attribute_values.set([self.v30])
        user_model = get_user_model()
        self.user = user_model.objects.create_superuser(
            "admin", "admin@example.com", "pass"
        )
        self.client = Client()
        self.client.force_login(self.user)

    def test_form_has_per_attribute_select(self):
        form = ProductAdminForm(instance=self.product)
        field_name = f"{ATTR_FIELD_PREFIX}{self.attr.pk}"
        self.assertIn(field_name, form.fields)
        self.assertNotIn("attribute_values", form.fields)
        self.assertEqual(form.fields[field_name].initial, self.v30.pk)

    def test_change_page_has_select_not_filter_horizontal(self):
        url = reverse("admin:catalog_product_change", args=[self.product.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        self.assertIn("Характеристики", html)
        self.assertIn(f'name="attr_select_{self.attr.pk}"', html)
        self.assertNotIn("Обрано Характеристики", html)
        self.assertNotIn("Choose all Характеристики", html)

    def test_save_attribute_via_select(self):
        form = ProductAdminForm(
            data={
                "sku": self.product.sku,
                "name_uk": self.product.name_uk,
                "price": "100.00",
                "stock": 0,
                "availability": self.product.availability,
                "status": self.product.status,
                "sort_order": 0,
                "popularity": 0,
                f"{ATTR_FIELD_PREFIX}{self.attr.pk}": str(self.v50.pk),
            },
            instance=self.product,
        )
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        form.save_attribute_values()
        self.assertEqual(
            list(self.product.attribute_values.values_list("pk", flat=True)),
            [self.v50.pk],
        )
