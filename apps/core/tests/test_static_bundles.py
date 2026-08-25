"""Тести збірки CSS-бандлів."""

from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

from apps.core.static_bundles import BUNDLE_SOURCES, build_bundles


class StaticBundlesTests(SimpleTestCase):
    def test_bundle_sources_exist(self):
        static_root = Path(settings.BASE_DIR) / "static"
        for bundle_name, sources in BUNDLE_SOURCES.items():
            for rel in sources:
                self.assertTrue(
                    (static_root / rel).is_file(),
                    msg=f"Missing source for {bundle_name}: {rel}",
                )

    def test_build_bundles_rewrites_font_urls(self):
        written = build_bundles(quiet=True)
        shell = next(p for p in written if p.name == "shell.css")
        text = shell.read_text(encoding="utf-8")
        self.assertIn("../../fonts/literata-cyrillic-400.woff2", text)
        self.assertNotIn('url("../fonts/literata', text)
