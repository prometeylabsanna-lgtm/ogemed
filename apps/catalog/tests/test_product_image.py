from decimal import Decimal
from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase, TestCase
from PIL import Image

from apps.catalog.forms import MIN_IMAGE_SIDE, ProductImageForm
from apps.catalog.models import Product, ProductImage


def _png(width: int, height: int) -> SimpleUploadedFile:
    buffer = BytesIO()
    Image.new("RGB", (width, height), color=(200, 180, 160)).save(buffer, format="PNG")
    return SimpleUploadedFile("shot.png", buffer.getvalue(), content_type="image/png")


class ProductImageFormTests(SimpleTestCase):
    def test_accepts_small_upload(self):
        form = ProductImageForm(data={}, files={"image": _png(800, 600)})
        form.is_valid()
        self.assertNotIn("image", form.errors)

    def test_accepts_large_enough_upload(self):
        form = ProductImageForm(data={}, files={"image": _png(MIN_IMAGE_SIDE, 1200)})
        form.is_valid()
        # продукт не заданий — але саме image має пройти перевірку
        self.assertNotIn("image", form.errors)


class ProductImageMainExclusiveTests(TestCase):
    def test_only_one_main_image(self):
        product = Product.objects.create(
            slug="img-main",
            sku="IMG-MAIN-1",
            name_uk="Тест",
            price=Decimal("10.00"),
        )
        first = ProductImage.objects.create(
            product=product,
            image=_png(MIN_IMAGE_SIDE, 1200),
            is_main=True,
        )
        second = ProductImage.objects.create(
            product=product,
            image=_png(MIN_IMAGE_SIDE, 1200),
            is_main=True,
        )
        first.refresh_from_db()
        second.refresh_from_db()
        self.assertFalse(first.is_main)
        self.assertTrue(second.is_main)
        self.assertEqual(product.images.filter(is_main=True).count(), 1)
