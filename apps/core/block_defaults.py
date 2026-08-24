"""Дефолти та лейбли SiteBlock для Cosmetics / OGEMED."""

from __future__ import annotations

BLOCK_FIELD_LABELS: dict[tuple[str, str], str] = {
    # Home — hero
    ("home", "hero_section_visible"): "Показувати hero",
    ("home", "hero_fallback_title"): "Fallback заголовок (без слайдів)",
    ("home", "hero_fallback_subtitle"): "Fallback підзаголовок",
    # Home — benefits
    ("home", "benefits_section_visible"): "Показувати переваги",
    ("home", "benefits_section_title"): "Заголовок секції",
    ("home", "benefit_1_title"): "Перевага 1 — заголовок",
    ("home", "benefit_1_text"): "Перевага 1 — текст",
    ("home", "benefit_2_title"): "Перевага 2 — заголовок",
    ("home", "benefit_2_text"): "Перевага 2 — текст",
    ("home", "benefit_3_title"): "Перевага 3 — заголовок",
    ("home", "benefit_3_text"): "Перевага 3 — текст",
    ("home", "benefit_4_title"): "Перевага 4 — заголовок",
    ("home", "benefit_4_text"): "Перевага 4 — текст",
    # Home — categories / products / brands / care / promo
    ("home", "categories_section_visible"): "Показувати швидкі категорії",
    ("home", "categories_section_title"): "Заголовок категорій",
    ("home", "products_section_visible"): "Показувати новинки/хіти",
    ("home", "products_new_title"): "Заголовок «Новинки»",
    ("home", "products_hits_title"): "Заголовок «Хіти»",
    ("home", "brands_section_visible"): "Показувати вітрину брендів",
    ("home", "brands_section_title"): "Заголовок брендів",
    ("home", "care_section_visible"): "Показувати підбір догляду",
    ("home", "care_section_title"): "Заголовок підбору",
    ("home", "care_section_text"): "Текст підбору",
    ("home", "care_cta_label"): "CTA підбору",
    ("home", "care_cta_url"): "URL CTA підбору",
    ("home", "promo_section_visible"): "Показувати промо",
    ("home", "promo_title"): "Промо — заголовок",
    ("home", "promo_url"): "Промо — URL",
    ("home", "promo_countdown"): "Промо — дата кінця (ISO)",
    ("home", "promo_image"): "Промо — зображення",
    # Catalog
    ("catalog", "seo_h1"): "H1",
    ("catalog", "seo_title"): "Meta title",
    ("catalog", "seo_description"): "Meta description",
    ("catalog", "seo_intro"): "SEO-текст",
    ("catalog", "filter_brands_open"): "Бренди — відкриті за замовч.",
    ("catalog", "filter_attrs_open"): "Атрибути — відкриті за замовч.",
    ("catalog", "filter_price_open"): "Ціна — відкрита за замовч.",
    # Shipping
    ("shipping", "methods_section_visible"): "Показувати методи доставки",
    ("shipping", "np_title"): "Нова Пошта — назва",
    ("shipping", "np_text"): "Нова Пошта — умови",
    ("shipping", "ukrposhta_title"): "Укрпошта — назва",
    ("shipping", "ukrposhta_text"): "Укрпошта — умови",
    ("shipping", "courier_title"): "Курʼєр — назва",
    ("shipping", "courier_text"): "Курʼєр — умови",
    ("shipping", "payment_section_visible"): "Показувати оплату",
    ("shipping", "pay_card_title"): "Картка — назва",
    ("shipping", "pay_card_text"): "Картка — опис",
    ("shipping", "pay_cod_title"): "Накладений — назва",
    ("shipping", "pay_cod_text"): "Накладений — опис",
    ("shipping", "pay_fop_title"): "ФОП — назва",
    ("shipping", "pay_fop_text"): "ФОП — опис",
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
    ("home", "benefits_section_visible"): ("1", "1"),
    ("home", "benefits_section_title"): ("Чому обирають нас", "Почему выбирают нас"),
    ("home", "benefit_1_title"): ("Оригінал", "Оригинал"),
    ("home", "benefit_1_text"): (
        "Працюємо з перевіреними брендами та офіційними постачальниками.",
        "Работаем с проверенными брендами и официальными поставщиками.",
    ),
    ("home", "benefit_2_title"): ("Швидка доставка", "Быстрая доставка"),
    ("home", "benefit_2_text"): (
        "Нова Пошта та курʼєр по Україні.",
        "Новая Почта и курьер по Украине.",
    ),
    ("home", "benefit_3_title"): ("Консультація", "Консультация"),
    ("home", "benefit_3_text"): (
        "Допоможемо підібрати догляд під ваш тип шкіри.",
        "Поможем подобрать уход под ваш тип кожи.",
    ),
    ("home", "benefit_4_title"): ("Безпечна оплата", "Безопасная оплата"),
    ("home", "benefit_4_text"): (
        "LiqPay, накладений платіж або реквізити ФОП.",
        "LiqPay, наложенный платеж или реквизиты ФОП.",
    ),
    ("home", "categories_section_visible"): ("1", "1"),
    ("home", "categories_section_title"): ("Категорії", "Категории"),
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
    ("home", "promo_section_visible"): ("0", "0"),
    ("home", "promo_title"): ("Спеціальна пропозиція", "Специальное предложение"),
    ("home", "promo_url"): ("/katalog/", "/katalog/"),
    ("home", "promo_countdown"): ("", ""),
    ("catalog", "seo_h1"): ("Каталог", "Каталог"),
    ("catalog", "seo_title"): (
        "Каталог косметики — OGEMED for you",
        "Каталог косметики — OGEMED for you",
    ),
    ("catalog", "seo_description"): (
        "Оригінальна косметика з доставкою по Україні.",
        "Оригинальная косметика с доставкой по Украине.",
    ),
    ("catalog", "seo_intro"): ("", ""),
    ("catalog", "filter_brands_open"): ("1", "1"),
    ("catalog", "filter_attrs_open"): ("1", "1"),
    ("catalog", "filter_price_open"): ("0", "0"),
    ("shipping", "methods_section_visible"): ("1", "1"),
    ("shipping", "np_title"): ("Нова Пошта", "Новая Почта"),
    ("shipping", "np_text"): (
        "Відділення або поштомат. Термін 1–3 дні.",
        "Отделение или почтомат. Срок 1–3 дня.",
    ),
    ("shipping", "ukrposhta_title"): ("Укрпошта", "Укрпочта"),
    ("shipping", "ukrposhta_text"): (
        "Доставка у відділення по Україні.",
        "Доставка в отделение по Украине.",
    ),
    ("shipping", "courier_title"): ("Курʼєр", "Курьер"),
    ("shipping", "courier_text"): (
        "Адресна доставка у вашому місті (за наявності).",
        "Адресная доставка в вашем городе (при наличии).",
    ),
    ("shipping", "payment_section_visible"): ("1", "1"),
    ("shipping", "pay_card_title"): ("Онлайн карткою", "Онлайн картой"),
    ("shipping", "pay_card_text"): (
        "Безпечна оплата через LiqPay.",
        "Безопасная оплата через LiqPay.",
    ),
    ("shipping", "pay_cod_title"): ("При отриманні", "При получении"),
    ("shipping", "pay_cod_text"): (
        "Готівка або карта у відділенні / курʼєру.",
        "Наличные или карта в отделении / курьеру.",
    ),
    ("shipping", "pay_fop_title"): ("На реквізити ФОП", "На реквизиты ФОП"),
    ("shipping", "pay_fop_text"): (
        "Реквізити надсилаємо після оформлення.",
        "Реквизиты отправляем после оформления.",
    ),
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
    ("home", "promo_image"): "image",
    ("home", "care_cta_url"): "url",
    ("home", "promo_url"): "url",
}

MULTILINE_KEYS: frozenset[str] = frozenset({
    "hero_fallback_subtitle",
    "benefit_1_text",
    "benefit_2_text",
    "benefit_3_text",
    "benefit_4_text",
    "care_section_text",
    "seo_description",
    "seo_intro",
    "np_text",
    "ukrposhta_text",
    "courier_text",
    "pay_card_text",
    "pay_cod_text",
    "pay_fop_text",
    "intro_text",
    "footer_about_text",
})

INLINE_KEYS: frozenset[str] = frozenset({
    "hero_fallback_title",
    "benefits_section_title",
    "benefit_1_title",
    "benefit_2_title",
    "benefit_3_title",
    "benefit_4_title",
    "categories_section_title",
    "products_new_title",
    "products_hits_title",
    "brands_section_title",
    "care_section_title",
    "care_cta_label",
    "promo_title",
    "promo_countdown",
    "seo_h1",
    "seo_title",
    "np_title",
    "ukrposhta_title",
    "courier_title",
    "pay_card_title",
    "pay_cod_title",
    "pay_fop_title",
    "intro_title",
    "cta_label",
    "header_search_placeholder",
    "footer_copyright",
    "care_cta_url",
    "promo_url",
})

VISIBILITY_SUFFIX = "_visible"


def is_visibility_key(key: str) -> bool:
    return key.endswith(VISIBILITY_SUFFIX) or key.endswith("_open")


def default_pair(page: str, key: str) -> tuple[str, str]:
    return BLOCK_DEFAULTS.get((page, key), ("", ""))
