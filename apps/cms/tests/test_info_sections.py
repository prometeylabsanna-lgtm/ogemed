"""Тести редакторів секцій інфо-сторінок."""
from django.test import TestCase
from django.urls import reverse

from apps.cms.info_page_models import InfoPageSection
from apps.cms.info_page_service import sections_for_page
from apps.cms.models import CMSPage


class InfoPageSectionsTests(TestCase):
    def setUp(self):
        InfoPageSection.objects.create(
            page_key="privacy",
            layout=InfoPageSection.Layout.PROSE,
            heading_uk="Тест секція",
            heading_ru="Тест секция",
            body_uk="<p>Текст UA</p>",
            body_ru="<p>Текст RU</p>",
            sort_order=0,
            is_active=True,
        )
        CMSPage.objects.create(
            slug="polityka-konfidentsiynosti",
            page_key="privacy",
            title_uk="Політика",
            title_ru="Политика",
            body_uk="",
            is_published=True,
        )

    def test_sections_from_db(self):
        rows = sections_for_page("privacy")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["title"], "Тест секція")
        self.assertIn("Текст UA", rows[0]["body"])

    def test_privacy_page_renders_section(self):
        r = self.client.get(reverse("cms:privacy"))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Тест секція")
        self.assertContains(r, "Текст UA")
