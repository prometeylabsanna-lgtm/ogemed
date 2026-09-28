from django.test import TestCase

from apps.catalog.models import Availability, Brand, Category, Product
from apps.cms.models import CMSPage
from apps.core.html_text import plain_text, sanitize_richtext
from apps.core.models import SiteBlock


class HtmlTextHelpersTests(TestCase):
    def test_plain_text_strips_visible_tags(self):
        self.assertEqual(plain_text("<p>Новинки</p>"), "Новинки")
        self.assertEqual(plain_text("<p>A</p><p>B</p>", single_line=True), "A B")
        self.assertEqual(plain_text("1"), "1")

    def test_richtext_keeps_markup_drops_script(self):
        html = sanitize_richtext(
            '<p>Hi <strong>x</strong></p><script>alert(1)</script><img src=x onerror=alert(1)>'
        )
        self.assertIn("<strong>x</strong>", html)
        self.assertNotIn("script", html.lower())
        self.assertNotIn("onerror", html.lower())
        self.assertNotIn("<img", html.lower())


class AdminHtmlSaveTests(TestCase):
    def test_cms_title_strips_tags_on_save(self):
        page = CMSPage.objects.create(
            slug="html-test",
            title_uk="<p>Заголовок</p>",
            body_uk="<p>Текст</p><script>alert(1)</script>",
            is_published=True,
        )
        page.refresh_from_db()
        self.assertEqual(page.title_uk, "Заголовок")
        self.assertIn("Текст", page.body_uk)
        self.assertNotIn("script", page.body_uk.lower())

    def test_site_block_plain_text_on_save(self):
        block, _ = SiteBlock.objects.update_or_create(
            page="home",
            key="products_new_title",
            defaults={
                "label": "Новинки",
                "text_html": "<p>Новинки</p>",
                "text_html_uk": "<p>Новинки</p>",
                "text_html_ru": "<p>Новинки</p>",
            },
        )
        block.refresh_from_db()
        self.assertEqual(block.text_html_uk, "Новинки")
        self.assertEqual(block.localized_text(), "Новинки")

    def test_product_description_renders_without_raw_tags(self):
        brand = Brand.objects.create(slug="b-html", name_uk="Brand")
        cat = Category.objects.create(slug="c-html", name_uk="Cat")
        product = Product.objects.create(
            slug="html-serum",
            name_uk="<p>Сироватка HTML</p>",
            brand=brand,
            primary_category=cat,
            availability=Availability.IN_STOCK,
            is_active=True,
            sku="HTML-SKU-1",
            price="10.00",
            stock=1,
            short_description_uk="<p>Коротко</p>",
            description_uk="<p>Повний <strong>опис</strong></p><script>x</script>",
        )
        product.refresh_from_db()
        self.assertEqual(product.name_uk, "Сироватка HTML")
        self.assertEqual(product.short_description, "Коротко")
        response = self.client.get(product.get_absolute_url())
        self.assertContains(response, "Сироватка HTML")
        self.assertContains(response, "опис")
        self.assertNotContains(response, "&lt;p&gt;")
        self.assertNotContains(response, "<script>")
        self.assertContains(response, "<strong>опис</strong>", html=False)
