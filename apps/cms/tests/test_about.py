from django.test import TestCase

from apps.cms.about_content import AboutContent
from apps.cms.models import CMSPage


class AboutPageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        CMSPage.objects.create(
            slug="pro-nas",
            page_key="about",
            title_uk="Про нас",
            title_ru="О нас",
            body_uk="",
            body_ru="",
            is_published=True,
        )
        AboutContent.objects.create(
            pk=1,
            hero_title_uk="Краса з турботою про вас",
            hero_title_ru="Красота с заботой о вас",
            history_title_uk="Як зʼявився OGEMED for you",
            history_title_ru="Как появился OGEMED for you",
            history_card_1_title_uk="Як зʼявився OGEMED for you",
            history_card_1_title_ru="Как появился OGEMED for you",
            history_card_1_body_uk="Текст картки 1.",
            history_card_2_title_uk="Що ми відбираємо для каталогу",
            history_card_2_body_uk="Текст картки 2.",
            history_card_3_title_uk="Як супроводжуємо замовлення",
            history_card_3_body_uk="Текст картки 3.",
            philosophy_title_uk="Менше шуму — більше уваги до шкіри",
            philosophy_title_ru="Меньше шума — больше внимания к коже",
            cta_title_uk="Готові знайти свій догляд?",
            cta_title_ru="Готовы найти свой уход?",
            cta_catalog_label_uk="До каталогу",
            cta_contacts_label_uk="Контакти",
        )

    def test_about_template_and_sections_uk(self):
        response = self.client.get("/pro-nas/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "cms/about.html")
        self.assertContains(response, "about-hero")
        self.assertContains(response, "about-hero__crumbs")
        self.assertContains(response, "Краса з турботою про вас")
        self.assertContains(response, "Як зʼявився OGEMED for you")
        self.assertContains(response, "about-paper")
        self.assertContains(response, "about-paper__card")
        self.assertContains(response, "Що ми відбираємо для каталогу")
        self.assertContains(response, "Як супроводжуємо замовлення")
        self.assertContains(response, "Менше шуму — більше уваги до шкіри")
        self.assertContains(response, "about-story")
        self.assertContains(response, "about-story__grid")
        self.assertContains(response, "about-philosophy__top")
        self.assertContains(response, "about-philosophy__motion")
        self.assertContains(response, "about-philosophy__values")
        self.assertContains(response, "about-value")
        self.assertContains(response, "about-value-modal")
        self.assertContains(response, "data-value-trigger")
        self.assertContains(response, "Турбота")
        self.assertContains(response, "Довіра")
        self.assertContains(response, "Баланс")
        self.assertContains(response, "Впевнений вибір")
        self.assertContains(response, "img/about/history-paper.png")
        self.assertContains(response, "about-paper__matte")
        self.assertContains(response, "about-paper__curl")
        self.assertContains(response, "about-paper__swipe")
        self.assertNotContains(response, "Потягніть за край картки")
        self.assertContains(response, "Готові знайти свій догляд?")
        self.assertContains(response, "/katalog/")
        self.assertContains(response, "/kontakty/")
        self.assertContains(response, "img/about/hero.jpg")
        # breadcrumbs лише на банері, не дублюються над hero
        self.assertEqual(response.content.decode().count('class="breadcrumbs"'), 1)

    def test_about_sections_ru(self):
        response = self.client.get("/ru/pro-nas/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Красота с заботой о вас")
        self.assertContains(response, "Как появился OGEMED for you")
        self.assertContains(response, "Меньше шума — больше внимания к коже")

    def test_about_singleton(self):
        obj = AboutContent.load()
        self.assertEqual(obj.pk, 1)
        AboutContent(hero_title_uk="dup").save()
        self.assertEqual(AboutContent.objects.count(), 1)

    def test_hidden_hero_section(self):
        about = AboutContent.load()
        about.hero_visible = False
        about.save(update_fields=["hero_visible"])
        response = self.client.get("/pro-nas/")
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'class="about-hero"')
        self.assertContains(response, "about-story")
        self.assertContains(response, "about-paper")
