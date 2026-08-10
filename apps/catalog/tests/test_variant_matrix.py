from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from apps.catalog.models import (
    Attribute,
    AttributeValue,
    Availability,
    Brand,
    Category,
    Product,
    ProductVariant,
)
from apps.catalog.variant_matrix import (
    build_variant_option_groups,
    resolve_variant_for_option,
    uses_flat_variant_labels,
)


class VariantMatrixUnitTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.brand = Brand.objects.create(slug="b", name_uk="B")
        cls.cat = Category.objects.create(slug="c", name_uk="C")
        cls.product = Product.objects.create(
            slug="matrix-serum",
            name_uk="Matrix",
            brand=cls.brand,
            primary_category=cls.cat,
            availability=Availability.IN_STOCK,
            is_active=True,
        )
        cls.vol = Attribute.objects.create(slug="obyem", name_uk="Обʼєм", sort_order=1)
        cls.col = Attribute.objects.create(slug="kolir", name_uk="Колір", sort_order=2)
        cls.v50 = AttributeValue.objects.create(
            attribute=cls.vol, slug="50", name_uk="50 мл", sort_order=1
        )
        cls.v100 = AttributeValue.objects.create(
            attribute=cls.vol, slug="100", name_uk="100 мл", sort_order=2
        )
        cls.clear = AttributeValue.objects.create(
            attribute=cls.col,
            slug="clear",
            name_uk="Безбарвний",
            color_hex="#F3F6F4",
            sort_order=1,
        )
        cls.green = AttributeValue.objects.create(
            attribute=cls.col,
            slug="green",
            name_uk="Зелений",
            color_hex="#3D6B4F",
            sort_order=2,
        )
        cls.a = ProductVariant.objects.create(
            product=cls.product, sku="M-50-C", price=Decimal("100"), stock=5, sort_order=0
        )
        cls.b = ProductVariant.objects.create(
            product=cls.product, sku="M-50-G", price=Decimal("110"), stock=5, sort_order=1
        )
        cls.c = ProductVariant.objects.create(
            product=cls.product, sku="M-100-C", price=Decimal("150"), stock=5, sort_order=2
        )
        cls.a.attribute_values.set([cls.v50, cls.clear])
        cls.b.attribute_values.set([cls.v50, cls.green])
        cls.c.attribute_values.set([cls.v100, cls.clear])

    def test_groups_and_swatch(self):
        variants = list(self.product.variants.filter(is_active=True).prefetch_related(
            "attribute_values__attribute"
        ))
        groups = build_variant_option_groups(variants, self.a)
        self.assertEqual(len(groups), 2)
        self.assertEqual(groups[0].attribute.slug, "obyem")
        self.assertTrue(groups[1].is_color)
        self.assertTrue(any(o.is_swatch for o in groups[1].options))
        self.assertFalse(uses_flat_variant_labels(variants, groups))

    def test_resolve_keeps_other_axis(self):
        variants = list(self.product.variants.filter(is_active=True).prefetch_related(
            "attribute_values__attribute"
        ))
        target, ok = resolve_variant_for_option(
            variants, self.a, self.vol.pk, self.v100.pk
        )
        self.assertTrue(ok)
        self.assertEqual(target.sku, "M-100-C")

    def test_pdp_renders_groups_and_attrs(self):
        self.product.attribute_values.set([self.v50, self.clear])
        url = reverse("catalog:product_detail", kwargs={"slug": "matrix-serum"})
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Обʼєм")
        self.assertContains(r, "Колір")
        self.assertContains(r, "Характеристики")
        self.assertContains(r, "pdp__swatch")
        self.assertContains(r, 'name="variant_id"')
        self.assertContains(r, f'value="{self.a.pk}"')
