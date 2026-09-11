from django.test import SimpleTestCase

from apps.core.templatetags.responsive_img import responsive_img


class _FakeStorage:
    def exists(self, name: str) -> bool:
        return False

    def url(self, name: str) -> str:
        return f"/media/{name}"


class _FakeFile:
    def __init__(self, url: str):
        self.url = url
        self.name = url.rsplit("/", 1)[-1]
        self.storage = _FakeStorage()


class ResponsiveImgTagTests(SimpleTestCase):
    def test_prefer_full_keeps_original_src(self):
        field = _FakeFile("/media/hero/hero-1.jpg")
        data = responsive_img(field, prefer_full=True)
        self.assertEqual(data["src"], "/media/hero/hero-1.jpg")
        self.assertFalse(data["defer_src"])

    def test_defer_src_flag(self):
        field = _FakeFile("/media/products/shot.jpg")
        data = responsive_img(field, defer_src=True)
        self.assertTrue(data["defer_src"])
        self.assertEqual(data["src"], "/media/products/shot.jpg")

    def test_thumb_only_skips_full_srcset(self):
        field = _FakeFile("/media/products/shot.webp")
        data = responsive_img(field, thumb_only=True)
        self.assertEqual(data["srcset"], "")
