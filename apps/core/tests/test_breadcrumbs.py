from django.test import SimpleTestCase

from apps.core.breadcrumbs import (
    BreadcrumbItem,
    build_breadcrumbs,
    translate_path_for_language,
)


class BreadcrumbsHelperTests(SimpleTestCase):
    def test_build_starts_with_home(self):
        crumbs = build_breadcrumbs(None, ("Каталог", None))
        self.assertEqual(crumbs[0].label, "Головна")
        self.assertIsNotNone(crumbs[0].url)
        self.assertEqual(crumbs[-1].label, "Каталог")
        self.assertTrue(crumbs[-1].is_current)

    def test_last_forced_current(self):
        crumbs = build_breadcrumbs(
            None,
            BreadcrumbItem(label="Каталог", url="/katalog/"),
            BreadcrumbItem(label="Товар", url="/tovar/x/"),
        )
        self.assertIsNone(crumbs[-1].url)

    def test_lang_path_uk_to_ru(self):
        self.assertEqual(translate_path_for_language("/pro-nas/", "ru"), "/ru/pro-nas/")
        self.assertEqual(translate_path_for_language("/ru/pro-nas/", "uk"), "/pro-nas/")
        self.assertEqual(translate_path_for_language("/", "ru"), "/ru/")
        self.assertEqual(translate_path_for_language("/ru/", "uk"), "/")
