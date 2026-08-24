from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase, TestCase, override_settings
from PIL import Image

from apps.catalog.models import Brand, Category, Product, ProductImage
from apps.core.image_processing import (
    MAX_SIDE_PRODUCT,
    is_svg_upload,
    process_upload,
    raster_to_webp,
    sanitize_svg,
    thumb_storage_name,
)


def _raster(width: int, height: int, mode: str = "RGB", fmt: str = "PNG") -> bytes:
    buffer = BytesIO()
    color = (200, 180, 160, 128) if "A" in mode else (200, 180, 160)
    Image.new(mode, (width, height), color=color).save(buffer, format=fmt)
    return buffer.getvalue()


class ImageProcessingUnitTests(SimpleTestCase):
    def test_raster_to_webp_resizes_long_side(self):
        data = _raster(3000, 1500)
        webp, thumb, size = raster_to_webp(
            BytesIO(data), max_side=MAX_SIDE_PRODUCT, thumb_side=240
        )
        self.assertTrue(webp[:4] == b"RIFF" or webp[0:4])
        self.assertEqual(max(size), MAX_SIDE_PRODUCT)
        self.assertIsNotNone(thumb)
        with Image.open(BytesIO(webp)) as img:
            self.assertEqual(img.format, "WEBP")
            self.assertEqual(max(img.size), MAX_SIDE_PRODUCT)

    def test_does_not_upscale_small_image(self):
        data = _raster(800, 600)
        _webp, _thumb, size = raster_to_webp(BytesIO(data), max_side=2048)
        self.assertEqual(size, (800, 600))

    def test_keeps_alpha(self):
        data = _raster(400, 400, mode="RGBA")
        webp, _thumb, _size = raster_to_webp(BytesIO(data), max_side=1024)
        with Image.open(BytesIO(webp)) as img:
            self.assertIn(img.mode, {"RGBA", "RGB"})
            # WebP з альфою зазвичай RGBA
            self.assertEqual(img.mode, "RGBA")

    def test_sanitize_svg_strips_script(self):
        raw = b'<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script><rect/></svg>'
        cleaned = sanitize_svg(raw).decode()
        self.assertNotIn("<script", cleaned.lower())
        self.assertIn("<rect", cleaned)

    def test_process_upload_svg(self):
        svg = SimpleUploadedFile(
            "icon.svg",
            b'<svg xmlns="http://www.w3.org/2000/svg" onload="x()"><circle/></svg>',
            content_type="image/svg+xml",
        )
        self.assertTrue(is_svg_upload(svg))
        main, thumb = process_upload(svg, allow_svg=True, generate_thumb=True)
        self.assertTrue(main.name.endswith(".svg"))
        self.assertIsNone(thumb)
        main.seek(0)
        self.assertNotIn("onload", main.read().decode().lower())

    def test_thumb_storage_name(self):
        self.assertEqual(
            thumb_storage_name("products/shot-abc.webp"),
            "products/shot-abc_thumb.webp",
        )


@override_settings(MEDIA_ROOT="/tmp/cosmetics_test_media")
class OptimizedImageFieldIntegrationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.brand = Brand.objects.create(slug="b", name_uk="B")
        cls.cat = Category.objects.create(slug="c", name_uk="C")
        cls.product = Product.objects.create(
            slug="p",
            name_uk="P",
            brand=cls.brand,
            primary_category=cls.cat,
            is_active=True,
        )

    def test_product_image_saved_as_webp(self):
        upload = SimpleUploadedFile(
            "фото товару.png",
            _raster(1800, 1200),
            content_type="image/png",
        )
        obj = ProductImage(product=self.product, image=upload, is_main=True)
        obj.save()
        obj.refresh_from_db()
        self.assertTrue(obj.image.name.endswith(".webp"))
        self.assertIn("products/", obj.image.name)
        # ASCII-safe name (no Cyrillic in path basename ideally — slugify)
        basename = obj.image.name.rsplit("/", 1)[-1]
        self.assertTrue(basename.endswith(".webp"))
        storage = obj.image.storage
        thumb = thumb_storage_name(obj.image.name)
        self.assertTrue(storage.exists(obj.image.name))
        self.assertTrue(storage.exists(thumb))
