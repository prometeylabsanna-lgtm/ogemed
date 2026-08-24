"""Підказки розмірів зображень / лімітів тексту для CMS."""
from __future__ import annotations

IMAGE_PROFILES: dict[str, str] = {
    "block_image": "Рекомендовано WebP/JPEG, ширина до 1600px.",
    "hero": "Desktop ≈ 1920×800, Mobile — обрізання по центру. WebP/JPEG.",
    "promo": "Банер ≈ 1200×400.",
}

TEXT_LIMITS: dict[str, str] = {
    "hero_fallback_title": "До 80 символів.",
    "benefits_section_title": "До 60 символів.",
    "seo_title": "До 60 символів.",
    "seo_description": "До 160 символів.",
}


def get_image_hint(profile: str) -> str:
    return IMAGE_PROFILES.get(profile, "")


def get_text_limit_hint(key: str) -> str:
    return TEXT_LIMITS.get(key, "")
