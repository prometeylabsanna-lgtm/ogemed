"""Vercel media resolve: /tmp uploads + bundle seed fallback."""
from pathlib import Path
from unittest.mock import patch

from django.test import SimpleTestCase

from config import vercel_media


class VercelMediaResolveTests(SimpleTestCase):
    def test_resolve_falls_back_to_bundle(self):
        # будь-який існуючий файл у media/ (seed)
        media = vercel_media.BUNDLE_MEDIA
        if not media.is_dir():
            self.skipTest("no media/ directory")
        sample = next((p for p in media.rglob("*") if p.is_file()), None)
        if sample is None:
            self.skipTest("no media files")
        rel = str(sample.relative_to(media))
        with patch.object(vercel_media, "RUNTIME_MEDIA", Path("/tmp/ogemed_media_test_empty")):
            found = vercel_media.resolve_media_path(rel)
        self.assertIsNotNone(found)
        self.assertEqual(found.resolve(), sample.resolve())

    def test_resolve_rejects_traversal(self):
        self.assertIsNone(vercel_media.resolve_media_path("../secrets.txt"))
