from django.test import TestCase
from django.urls import reverse

from apps.catalog.models import Category
from apps.cms.models import CMSPage
from apps.core.models import SiteSettings


class Phase1SmokeTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        SiteSettings.objects.create(
            pk=1,
            phone="+380664247233",
            phone_2="+380973086063",
            email="hello@ogemed.ua",
            telegram_consultant_url="https://t.me/ogemed",
        )
        Category.objects.create(
            slug="oblychchya",
            name_uk="Обличчя",
            name_ru="Лицо",
            is_active=True,
            sort_order=1,
        )
        CMSPage.objects.create(
            slug="pro-nas",
            page_key="about",
            title_uk="Про нас",
            title_ru="О нас",
            body_uk="Текст про бренд.",
            body_ru="Текст о бренде.",
            is_published=True,
        )
        CMSPage.objects.create(
            slug="kontakty",
            page_key="contacts",
            title_uk="Контакти",
            title_ru="Контакты",
            body_uk="Контактний текст.",
            body_ru="Контактный текст.",
            is_published=True,
        )

    def test_home_returns_200_without_breadcrumbs(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'class="breadcrumbs"')
        self.assertContains(response, "OGEMED")

    def test_about_page_has_breadcrumbs(self):
        response = self.client.get("/pro-nas/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'class="breadcrumbs"')
        self.assertContains(response, "Головна")
        self.assertContains(response, "Про нас")
        self.assertContains(response, 'aria-current="page"')

    def test_contacts_page_200(self):
        response = self.client.get(reverse("cms:contacts"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Контакти")

    def test_healthz(self):
        response = self.client.get("/healthz/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), "ok")

    def test_ru_mirror_about(self):
        response = self.client.get("/ru/pro-nas/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "О нас")
        self.assertContains(response, 'class="breadcrumbs"')

    def test_site_settings_in_context(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context["site_settings"])
        self.assertEqual(response.context["site_settings"].email, "hello@ogemed.ua")
        self.assertIn("uk", response.context["lang_urls"])
        self.assertIn("ru", response.context["lang_urls"])

    def test_site_settings_singleton(self):
        obj = SiteSettings.load()
        self.assertEqual(obj.pk, 1)
        duplicate = SiteSettings(phone="000")
        duplicate.save()
        self.assertEqual(SiteSettings.objects.count(), 1)
        self.assertEqual(SiteSettings.objects.get().pk, 1)

    def test_footer_has_category_and_header_phone(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Обличчя")
        self.assertContains(response, "/katalog/oblychchya/")
        self.assertContains(response, 'class="site-header__contact-phone"')
        self.assertContains(response, "+380664247233")
        self.assertContains(response, "+380973086063")
        self.assertContains(response, 'href="tel:+380664247233"')
        self.assertContains(response, 'href="tel:+380973086063"')

    def test_cookie_banner_present(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "data-cookie-banner")
        self.assertContains(response, "data-cookie-accept")
        self.assertContains(response, "Прийняти")

    def test_custom_404_page(self):
        from django.test import override_settings

        with override_settings(DEBUG=False):
            response = self.client.get("/no-such-page-ogemed-404/")
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "error-page", status_code=404)
        self.assertContains(response, "Сторінку не знайдено", status_code=404)
        self.assertContains(response, "На головну", status_code=404)
        self.assertContains(response, "До каталогу", status_code=404)
