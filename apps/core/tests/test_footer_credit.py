from django.test import TestCase, override_settings
from django.urls import reverse

from apps.cms.models import CMSPage
from apps.core.models import SiteSettings

CREDIT_URL = "https://www.prometeylabs.com/internet-shop-v2/"


class FooterDeveloperLinkTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        SiteSettings.objects.create(
            pk=1,
            phone="+380 44 123 45 67",
            email="hello@ogemed.ua",
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
            slug="polityka-konfidentsiynosti",
            page_key="privacy",
            title_uk="Політика конфіденційності",
            title_ru="Политика конфиденциальности",
            body_uk="Privacy UA.",
            body_ru="Privacy RU.",
            is_published=True,
        )

    def test_home_has_nofollow_credit_link(self):
        response = self.client.get(reverse("core:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, CREDIT_URL)
        self.assertContains(response, "nofollow")
        self.assertContains(response, ">PrometeyLabs</a>")
        self.assertContains(response, "site-footer__credit-link")

    def test_localized_home_keeps_credit_link(self):
        response = self.client.get("/ru/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, CREDIT_URL)
        self.assertContains(response, "nofollow")
        self.assertContains(response, "site-footer__credit-link")

    def test_inner_pages_show_credit_without_link(self):
        for url in (reverse("cms:about"), reverse("cms:privacy")):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "PrometeyLabs")
            self.assertNotContains(response, CREDIT_URL)
            self.assertNotContains(response, "site-footer__credit-link")
            self.assertContains(response, "site-footer__credit-name")

    def test_404_footer_has_no_agency_link(self):
        with override_settings(DEBUG=False):
            response = self.client.get("/no-such-page-footer-credit-404/")
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "PrometeyLabs", status_code=404)
        self.assertNotContains(response, CREDIT_URL, status_code=404)
        self.assertNotContains(response, "site-footer__credit-link", status_code=404)
