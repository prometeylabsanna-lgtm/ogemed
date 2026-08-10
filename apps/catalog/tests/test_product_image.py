from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase
from PIL import Image

from apps.catalog.forms import MIN_IMAGE_SIDE, ProductImageForm


def _png(width: int, height: int) -> SimpleUploadedFile:
    buffer = BytesIO()
    Image.new("RGB", (width, height), color=(200, 180, 160)).save(buffer, format="PNG")
    return SimpleUploadedFile("shot.png", buffer.getvalue(), content_type="image/png")


class ProductImageFormTests(SimpleTestCase):
    def test_rejects_small_upload(self):
        form = ProductImageForm(data={}, files={"image": _png(800, 600)})
        self.assertFalse(form.is_valid())
        self.assertIn("image", form.errors)
        self.assertIn(str(MIN_IMAGE_SIDE), form.errors["image"][0])

    def test_accepts_large_enough_upload(self):
        form = ProductImageForm(data={}, files={"image": _png(MIN_IMAGE_SIDE, 1200)})
        form.is_valid()
        # продукт не заданий — але саме image має пройти перевірку розміру
        self.assertNotIn("image", form.errors)
