"""Підказки розмірів зображень / лімітів тексту для всієї адмінки."""
from __future__ import annotations

IMAGE_FORMAT_WEIGHT = (
    "Формат: JPG, PNG або WebP. Вага до 20 МБ (краще до 3 МБ)."
)

IMAGE_PROFILES: dict[str, str] = {
    "product": (
        "Картка/галерея: ≥1600 px по довгій стороні, пропорції ≈3∶4 "
        "(інакше краї обріжуться). "
        f"{IMAGE_FORMAT_WEIGHT}"
    ),
    "hero": (
        "Банер: Desktop ≈1920×800; на мобільному обрізання по центру. "
        f"{IMAGE_FORMAT_WEIGHT}"
    ),
    "block_image": (
        f"Рекомендовано ширину до 1600 px. {IMAGE_FORMAT_WEIGHT}"
    ),
    "care_section_image": (
        "Фон секції ≈1920×600. Без фото секція лишається без фону. "
        f"{IMAGE_FORMAT_WEIGHT}"
    ),
    "category": (
        "Обкладинка категорії ≈1200×1600 (3∶4) або квадрат від 1200 px. "
        f"{IMAGE_FORMAT_WEIGHT}"
    ),
    "brand_cover": (
        "Плитка в каталозі брендів ≈1200×1600 (3∶4). "
        f"{IMAGE_FORMAT_WEIGHT}"
    ),
    "brand_showcase": (
        "Вітрина на головній: краще PNG з прозорим фоном, довша сторона ≥1200 px. "
        f"{IMAGE_FORMAT_WEIGHT}"
    ),
    "logo": (
        "Логотип: PNG або SVG з прозорим фоном, читабельний у маленькому розмірі. "
        "Вага до 2 МБ."
    ),
    "label_icon": (
        "PNG з прозорим фоном, квадрат ≈128–256 px. Вага до 1 МБ."
    ),
    "about_hero": (
        "Банер «Про нас»: Desktop ≈1920×800; на мобільному обрізання по центру. "
        f"{IMAGE_FORMAT_WEIGHT}"
    ),
}

# Мʼякі ліміти для верстки (можуть бути менші за max_length поля).
TEXT_SOFT_LIMITS: dict[str, int] = {
    "hero_fallback_title": 80,
    "hero_fallback_subtitle": 140,
    "products_new_title": 40,
    "products_hits_title": 40,
    "brands_section_title": 40,
    "care_section_title": 60,
    "care_section_text": 200,
    "care_cta_label": 32,
    "intro_title": 60,
    "intro_text": 220,
    "cta_label": 40,
    "header_search_placeholder": 48,
    "footer_about_text": 200,
    "footer_copyright": 80,
    "title": 80,
    "subtitle": 120,
    "cta_title": 80,
    "cta_text": 220,
    "cta_catalog_label": 32,
    "cta_contacts_label": 32,
    "heading": 80,
    "subheading": 120,
    "note_title": 60,
    "note_text": 280,
    "hero_kicker": 40,
    "hero_title": 80,
    "hero_text": 220,
    "history_kicker": 40,
    "history_card_1_title": 60,
    "history_card_2_title": 60,
    "history_card_3_title": 60,
    "history_card_1_body": 600,
    "history_card_2_body": 600,
    "history_card_3_body": 600,
    "philosophy_kicker": 40,
    "philosophy_title": 80,
    "philosophy_body": 800,
    "philosophy_thesis_1_title": 40,
    "philosophy_thesis_2_title": 40,
    "philosophy_thesis_3_title": 40,
    "philosophy_thesis_4_title": 40,
    "philosophy_thesis_1_text": 160,
    "philosophy_thesis_2_text": 160,
    "philosophy_thesis_3_text": 160,
    "philosophy_thesis_4_text": 160,
    "name": 90,
    "short_description": 180,
    "tagline": 160,
    "alt": 120,
    "seo_title": 60,
    "seo_description": 160,
    "brand_tagline": 100,
    "sku": 64,
}

# Підписи без слова CTA (для редактора контенту).
FIELD_LABEL_OVERRIDES: dict[str, str] = {
    "cta_label_uk": "Текст кнопки (UK)",
    "cta_label_ru": "Текст кнопки (RU)",
    "cta_url": "Посилання кнопки",
    "cta_title_uk": "Заголовок форми (UK)",
    "cta_title_ru": "Заголовок форми (RU)",
    "cta_text_uk": "Текст форми (UK)",
    "cta_text_ru": "Текст форми (RU)",
    "cta_catalog_label_uk": "Кнопка «До каталогу» (UK)",
    "cta_catalog_label_ru": "Кнопка «До каталогу» (RU)",
    "cta_contacts_label_uk": "Кнопка «Контакти» (UK)",
    "cta_contacts_label_ru": "Кнопка «Контакти» (RU)",
    "cta_visible": "Показувати нижній блок з кнопками",
}

IMAGE_FIELD_PROFILES: dict[str, str] = {
    "image": "product",
    "hero_image": "about_hero",
    "history_image": "block_image",
    "cover_image": "brand_cover",
    "showcase_image": "brand_showcase",
    "logo": "logo",
}

TEXT_LIMITS: dict[str, str] = {
    "hero_fallback_title": "До 80 символів. Показується лише коли немає активних слайдів.",
    "hero_fallback_subtitle": "Короткий текст під заголовком, якщо немає слайдів (до 140).",
}


def normalize_field_key(name: str) -> str:
    if name.endswith("_uk") or name.endswith("_ru"):
        return name[:-3]
    return name


def get_image_hint(profile: str) -> str:
    return IMAGE_PROFILES.get(profile, "")


def get_text_soft_limit(key: str) -> int | None:
    base = normalize_field_key(key)
    return TEXT_SOFT_LIMITS.get(base) or TEXT_SOFT_LIMITS.get(key)


def get_text_limit_hint(key: str, *, max_length: int | None = None) -> str:
    if key in TEXT_LIMITS:
        hint = TEXT_LIMITS[key]
    else:
        soft = get_text_soft_limit(key)
        if soft:
            hint = (
                f"Рекомендовано до {soft} символів — довше може зламати верстку."
            )
        else:
            hint = ""
    if max_length and max_length > 0:
        hard = f"Максимум {max_length} символів."
        if hard not in hint:
            hint = f"{hint} {hard}".strip() if hint else hard
    return hint


def get_field_label_override(name: str) -> str:
    return FIELD_LABEL_OVERRIDES.get(name, "")
