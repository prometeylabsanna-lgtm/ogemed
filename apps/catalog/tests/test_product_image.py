from decimal import Decimal
from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, SimpleTestCase, TestCase
from django.urls import reverse
from PIL import Image

from apps.catalog.forms import MIN_IMAGE_SIDE, ProductImageForm
from apps.catalog.models import Product, ProductImage


def _png(width: int, height: int) -> SimpleUploadedFile:
    buffer = BytesIO()
    Image.new("RGB", (width, height), color=(200, 180, 160)).save(buffer, format="PNG")
    return SimpleUploadedFile("shot.png", buffer.getvalue(), content_type="image/png")


class ProductImageFormTests(SimpleTestCase):
    def test_image_not_required_for_html_submit(self):
        # Unfold ховає file input у display:none — required блокував би Save мовчки.
        form = ProductImageForm()
        self.assertFalse(form.fields["image"].required)

    def test_accepts_empty_image(self):
        form = ProductImageForm(data={"alt_uk": "", "is_main": False, "sort_order": 0})
        form.is_valid()
        self.assertNotIn("image", form.errors)

    def test_accepts_small_upload(self):
        form = ProductImageForm(data={}, files={"image": _png(800, 600)})
        form.is_valid()
        self.assertNotIn("image", form.errors)

    def test_accepts_large_enough_upload(self):
        form = ProductImageForm(data={}, files={"image": _png(MIN_IMAGE_SIDE, 1200)})
        form.is_valid()
        # продукт не заданий — але саме image має пройти перевірку
        self.assertNotIn("image", form.errors)


class ProductAdminAddWithoutImageTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_superuser(
            "admin", "admin@example.com", "pass"
        )
        self.client = Client()
        self.client.force_login(self.user)

    def test_add_page_file_input_not_required(self):
        url = reverse("admin:catalog_product_add")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        self.assertNotRegex(
            html,
            r'<input[^>]*type="file"[^>]*name="[^"]*image"[^>]*required',
        )
        self.assertNotRegex(
            html,
            r'<input[^>]*name="[^"]*image"[^>]*type="file"[^>]*required',
        )
        self.assertEqual(html.count("js/admin/product_image_main.js"), 1)

    def test_can_save_new_product_without_image(self):
        url = reverse("admin:catalog_product_add")
        get_resp = self.client.get(url)
        self.assertEqual(get_resp.status_code, 200)
        html = get_resp.content.decode()
        prefix = "images"
        if 'name="productimage_set-TOTAL_FORMS"' in html:
            prefix = "productimage_set"
        data = {
            "sku": "SAVE-NO-IMG",
            "barcode": "",
            "price": "99.00",
            "old_price": "",
            "wholesale_price": "",
            "stock": "1",
            "availability": "in_stock",
            "status": "active",
            "brand": "",
            "primary_category": "",
            "name_uk": "Товар без фото",
            "name_ru": "",
            "short_description_uk": "",
            "short_description_ru": "",
            "description_uk": "",
            "description_ru": "",
            "seo_title_uk": "",
            "seo_title_ru": "",
            "seo_description_uk": "",
            "seo_description_ru": "",
            "sort_order": "0",
            "is_hit": False,
            "is_new": False,
            "is_sale": False,
            f"{prefix}-TOTAL_FORMS": "1",
            f"{prefix}-INITIAL_FORMS": "0",
            f"{prefix}-MIN_NUM_FORMS": "0",
            f"{prefix}-MAX_NUM_FORMS": "1000",
            f"{prefix}-0-id": "",
            f"{prefix}-0-image": "",
            f"{prefix}-0-alt_uk": "",
            f"{prefix}-0-alt_ru": "",
            f"{prefix}-0-is_main": False,
            "_save": "Save",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302, response.content[:800])
        self.assertTrue(Product.objects.filter(sku="SAVE-NO-IMG").exists())


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
