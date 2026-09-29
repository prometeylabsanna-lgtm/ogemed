"""Тести єдиного body юридичних сторінок (без секцій-карток)."""
from django.test import TestCase
from django.urls import reverse

from apps.cms.info_page_models import InfoPageMeta, InfoPageSection
from apps.cms.info_page_service import merge_sections_html_for_page
from apps.cms.models import CMSPage


class LegalPageBodyTests(TestCase):
    def setUp(self):
        InfoPageSection.objects.filter(page_key="privacy").delete()
        InfoPageSection.objects.create(
            page_key="privacy",
            layout=InfoPageSection.Layout.PROSE,
            heading_uk="Стара секція",
            heading_ru="Старая секция",
            body_uk="<p>Секція UA</p>",
            body_ru="<p>Секция RU</p>",
            sort_order=0,
            is_active=True,
        )
        self.page, _ = CMSPage.objects.update_or_create(
            slug="polityka-konfidentsiynosti",
            defaults={
                "page_key": "privacy",
                "title_uk": "Політика",
                "title_ru": "Политика",
                "body_uk": "<h2>Єдиний текст</h2><p>Основний контент UA</p>",
                "body_ru": "<h2>Единый текст</h2><p>Основной контент RU</p>",
                "is_published": True,
            },
        )
        InfoPageMeta.objects.update_or_create(
            page_key="privacy",
            defaults={
                "cta_title_uk": "Форма заголовок",
                "cta_text_uk": "Форма текст",
            },
        )

    def test_merge_sections_html(self):
        html = merge_sections_html_for_page("privacy", lang="uk")
        self.assertIn("<h2>Стара секція</h2>", html)
        self.assertIn("Секція UA", html)

    def test_privacy_renders_body_not_sections(self):
        r = self.client.get(reverse("cms:privacy"))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Єдиний текст")
        self.assertContains(r, "Основний контент UA")
        self.assertNotContains(r, "Стара секція")
        self.assertContains(r, "Форма заголовок")
