"""Дефолти та лейбли SiteBlock для Cosmetics / OGEMED."""

from __future__ import annotations

BLOCK_FIELD_LABELS: dict[tuple[str, str], str] = {
    # Home — hero
    ("home", "hero_section_visible"): "Показувати hero",
    ("home", "hero_fallback_title"): "Заголовок без слайдів",
    ("home", "hero_fallback_subtitle"): "Підзаголовок без слайдів",
    # Home — products / brands / care
    ("home", "products_section_visible"): "Показувати новинки/хіти",
    ("home", "products_new_title"): "Заголовок «Новинки»",
    ("home", "products_hits_title"): "Заголовок «Хіти»",
    ("home", "brands_section_visible"): "Показувати вітрину брендів",
    ("home", "brands_section_title"): "Заголовок брендів",
    ("home", "care_section_visible"): "Показувати підбір догляду",
    ("home", "care_section_title"): "Заголовок підбору",
    ("home", "care_section_text"): "Текст підбору",
    ("home", "care_section_image"): "Фон секції підбору",
    ("home", "care_cta_label"): "CTA підбору",
    ("home", "care_cta_url"): "URL CTA підбору",
    # Contacts
    ("contacts", "intro_title"): "Заголовок intro",
    ("contacts", "intro_text"): "Текст intro",
    ("contacts", "cta_label"): "CTA «Передзвоніть»",
    # Site chrome
    ("site", "header_search_placeholder"): "Placeholder пошуку",
    ("site", "footer_about_text"): "Опис у підвалі",
    ("site", "footer_copyright"): "Копірайт",
}

# (uk, ru) — для seed і get_or_create
BLOCK_DEFAULTS: dict[tuple[str, str], tuple[str, str]] = {
    ("home", "hero_section_visible"): ("1", "1"),
    ("home", "hero_fallback_title"): (
        "Косметика з турботою про вас",
        "Косметика с заботой о вас",
    ),
    ("home", "hero_fallback_subtitle"): (
        "OGEMED for you — догляд, якому можна довіряти",
        "OGEMED for you — уход, которому можно доверять",
    ),
    ("home", "products_section_visible"): ("1", "1"),
    ("home", "products_new_title"): ("Новинки", "Новинки"),
    ("home", "products_hits_title"): ("Хіти", "Хиты"),
    ("home", "brands_section_visible"): ("1", "1"),
    ("home", "brands_section_title"): ("Бренди", "Бренды"),
    ("home", "care_section_visible"): ("1", "1"),
    ("home", "care_section_title"): (
        "Знайдіть свій ідеальний догляд",
        "Найдите свой идеальный уход",
    ),
    ("home", "care_section_text"): (
        "Оберіть категорію або бренд — і зберіть свою рутину.",
        "Выберите категорию или бренд — и соберите свою рутину.",
    ),
    ("home", "care_cta_label"): ("До каталогу", "В каталог"),
    ("home", "care_cta_url"): ("/katalog/", "/katalog/"),
    ("contacts", "intro_title"): ("Контакти", "Контакты"),
    ("contacts", "intro_text"): (
        "Напишіть або зателефонуйте — відповімо протягом робочого дня.",
        "Напишите или позвоните — ответим в течение рабочего дня.",
    ),
    ("contacts", "cta_label"): ("Передзвоніть мені", "Перезвоните мне"),
    ("site", "header_search_placeholder"): (
        "Пошук за назвою або артикулом",
        "Поиск по названию или артикулу",
    ),
    ("site", "footer_about_text"): (
        "OGEMED for you — косметика з турботою про вас.",
        "OGEMED for you — косметика с заботой о вас.",
    ),
    ("site", "footer_copyright"): (
        "© OGEMED for you. Усі права захищені.",
        "© OGEMED for you. Все права защищены.",
    ),
}

BLOCK_CONTENT_TYPES: dict[tuple[str, str], str] = {
    ("home", "care_section_image"): "image",
    ("home", "care_cta_url"): "url",
}

MULTILINE_KEYS: frozenset[str] = frozenset({
    "hero_fallback_subtitle",
    "care_section_text",
    "intro_text",
    "footer_about_text",
})

INLINE_KEYS: frozenset[str] = frozenset({
    "hero_fallback_title",
    "products_new_title",
    "products_hits_title",
    "brands_section_title",
    "care_section_title",
    "care_cta_label",
    "intro_title",
    "cta_label",
    "header_search_placeholder",
    "footer_copyright",
    "care_cta_url",
})

VISIBILITY_SUFFIX = "_visible"


def is_visibility_key(key: str) -> bool:
    return key.endswith(VISIBILITY_SUFFIX) or key.endswith("_open")


def default_pair(page: str, key: str) -> tuple[str, str]:
    return BLOCK_DEFAULTS.get((page, key), ("", ""))
