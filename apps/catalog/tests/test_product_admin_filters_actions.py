"""Фільтри та масові дії товарів в адмінці."""
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from apps.catalog.models import Attribute, AttributeValue, Product


class ProductAdminFiltersActionsTests(TestCase):
    def setUp(self):
        self.skin = Attribute.objects.create(
            slug="typ-shkiry", name_uk="Тип шкіри", sort_order=1
        )
        Attribute.objects.create(slug="typ-doglyadu", name_uk="Тип догляду", sort_order=2)
        Attribute.objects.create(slug="obyem", name_uk="Обʼєм", sort_order=3)
        Attribute.objects.create(slug="kraina", name_uk="Країна виробник", sort_order=4)
        self.dry = AttributeValue.objects.create(
            attribute=self.skin, slug="sukha", name_uk="Суха", sort_order=1
        )
        self.normal = AttributeValue.objects.create(
            attribute=self.skin, slug="normalna", name_uk="Нормальна", sort_order=2
        )
        self.p_dry = Product.objects.create(
            slug="p-dry", sku="D1", name_uk="Крем для сухої", price=10, is_hit=False
        )
        self.p_dry.attribute_values.set([self.dry])
        self.p_norm = Product.objects.create(
            slug="p-norm", sku="N1", name_uk="Крем для нормальної", price=10, is_hit=False
        )
        self.p_norm.attribute_values.set([self.normal])
        user_model = get_user_model()
        self.user = user_model.objects.create_superuser(
            "admin", "admin@example.com", "pass"
        )
        self.client = Client()
        self.client.force_login(self.user)

    def test_changelist_has_attribute_filters_and_actions(self):
        url = reverse("admin:catalog_product_changelist")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        self.assertIn("Тип шкіри", html)
        self.assertIn("Тип догляду", html)
        self.assertIn("Країна виробник", html)
        self.assertIn('value="mark_as_hit"', html)
        self.assertIn('value="mark_as_new"', html)
        self.assertIn('value="delete_selected"', html)

    def test_filter_by_skin_type(self):
        url = reverse("admin:catalog_product_changelist")
        response = self.client.get(url, {"attr_typ_shkiry": str(self.dry.pk)})
        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        self.assertIn("Крем для сухої", html)
        self.assertNotIn("Крем для нормальної", html)

    def test_bulk_mark_hit(self):
        url = reverse("admin:catalog_product_changelist")
        response = self.client.post(
            url,
            {
                "action": "mark_as_hit",
                "_selected_action": [str(self.p_dry.pk), str(self.p_norm.pk)],
                "index": 0,
            },
        )
        self.assertIn(response.status_code, (200, 302))
        self.p_dry.refresh_from_db()
        self.p_norm.refresh_from_db()
        self.assertTrue(self.p_dry.is_hit)
        self.assertTrue(self.p_norm.is_hit)
