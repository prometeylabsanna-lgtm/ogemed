"""Підказки розмірів зображень / лімітів тексту для CMS."""
from __future__ import annotations

IMAGE_PROFILES: dict[str, str] = {
    "block_image": "Рекомендовано WebP/JPEG, ширина до 1600px.",
    "hero": "Desktop ≈ 1920×800, Mobile — обрізання по центру. WebP/JPEG.",
    "care_section_image": (
        "Фон секції ≈ 1920×600, WebP/JPEG. Без фото секція лишається без фону."
    ),
}

TEXT_LIMITS: dict[str, str] = {
    "hero_fallback_title": "До 80 символів. Показується лише коли немає активних слайдів.",
    "hero_fallback_subtitle": "Короткий текст під заголовком, якщо немає слайдів.",
}


def get_image_hint(profile: str) -> str:
    return IMAGE_PROFILES.get(profile, "")


def get_text_limit_hint(key: str) -> str:
    return TEXT_LIMITS.get(key, "")
