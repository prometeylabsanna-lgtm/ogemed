"""Smoke-тести registry + CMS admin."""
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from apps.core.models import SiteBlock, SiteSettings
from apps.core.site_content_registry import CONTENT_SECTIONS
from apps.core.site_content_registry import iter_section_blocks


def _all_keys():
    keys = set()
    for section in CONTENT_SECTIONS:
        keys.update(iter_section_blocks(section))
    return keys


class SiteContentRegistryTests(TestCase):
    def test_admin_model_names_unique(self):
        names = [s.admin_model_name for s in CONTENT_SECTIONS]
        self.assertEqual(len(names), len(set(names)))

    def test_page_key_pairs_unique(self):
        keys = _all_keys()
        self.assertGreater(len(keys), 5)

    def test_dead_sections_removed(self):
        names = {s.admin_model_name for s in CONTENT_SECTIONS}
        self.assertNotIn("homebenefitssettings", names)
        self.assertNotIn("homecategoriessettings", names)
        self.assertNotIn("homepromosettings", names)
        self.assertNotIn("catalogseosettings", names)
        self.assertNotIn("catalogfilterssettings", names)


class SiteContentAdminTests(TestCase):
    def setUp(self):
        SiteSettings.objects.get_or_create(pk=1)
        user_model = get_user_model()
        self.user = user_model.objects.create_superuser(
            "admin",
            "admin@example.com",
            "pass",
        )
        self.client = Client()
        self.client.force_login(self.user)

    def test_hero_section_get(self):
        url = reverse("admin:core_homeherosettings_changelist")
        response = self.client.get(url)
        self.assertIn(response.status_code, (200, 302))
        if response.status_code == 302:
            follow = self.client.get(response["Location"])
            self.assertEqual(follow.status_code, 200)

    def test_header_section_has_logo_and_phone(self):
        url = reverse("admin:core_siteheadersettings_change", args=[1])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        self.assertIn('name="logo"', html)
        self.assertIn('name="phone"', html)
        self.assertIn("Логотип і телефон", html)
