"""UNFOLD sidebar для OGEMED.

Лінки — звичайні рядки (не reverse_lazy): Vercel серіалізує settings у JSON
і __str__ у Promise ламає AppRegistryNotReady.
Префікс береться з settings.ADMIN_URL.
"""
from __future__ import annotations

from django.conf import settings

from apps.core.site_content_registry import build_content_sidebar_items


def _admin_link(*parts: str) -> str:
    prefix = (getattr(settings, "ADMIN_URL", "admin") or "admin").strip("/")
    path = "/".join(p.strip("/") for p in parts if p)
    return f"/{prefix}/{path}/" if path else f"/{prefix}/"


def build_unfold_config() -> dict:
    return {
        "SITE_TITLE": "OGEMED Admin",
        "SITE_HEADER": "OGEMED for you",
        "SITE_SYMBOL": "spa",
        "SHOW_HISTORY": True,
        "SIDEBAR": {
            "show_search": True,
            "command_search": True,
            "show_all_applications": False,
            "navigation": [
                {
                    "title": "Налаштування",
                    "separator": True,
                    "items": [
                        {
                            "title": "Налаштування сайту",
                            "icon": "settings",
                            "link": _admin_link("core", "sitesettings"),
                        },
                    ],
                },
                {
                    "title": "Вміст сторінок",
                    "separator": True,
                    "collapsible": True,
                    "items": build_content_sidebar_items(),
                },
                {
                    "title": "Про нас (детально)",
                    "separator": True,
                    "items": [
                        {
                            "title": "Контент «Про нас»",
                            "icon": "info",
                            "link": _admin_link("cms", "aboutcontent"),
                        },
                        {
                            "title": "CMS-сторінки",
                            "icon": "article",
                            "link": _admin_link("cms", "cmspage"),
                        },
                    ],
                },
                {
                    "title": "Каталог",
                    "separator": True,
                    "collapsible": True,
                    "items": [
                        {
                            "title": "Товари",
                            "icon": "inventory_2",
                            "link": _admin_link("catalog", "product"),
                        },
                        {
                            "title": "Категорії",
                            "icon": "category",
                            "link": _admin_link("catalog", "category"),
                        },
                        {
                            "title": "Бренди",
                            "icon": "sell",
                            "link": _admin_link("catalog", "brand"),
                        },
                        {
                            "title": "Атрибути / фільтри",
                            "icon": "tune",
                            "link": _admin_link("catalog", "attribute"),
                        },
                        {
                            "title": "Варіанти",
                            "icon": "qr_code_2",
                            "link": _admin_link("catalog", "productvariant"),
                        },
                    ],
                },
                {
                    "title": "Продажі",
                    "separator": True,
                    "collapsible": True,
                    "items": [
                        {
                            "title": "Замовлення",
                            "icon": "shopping_cart",
                            "link": _admin_link("orders", "order"),
                        },
                        {
                            "title": "Ліди",
                            "icon": "support_agent",
                            "link": _admin_link("cms", "lead"),
                        },
                    ],
                },
                {
                    "title": "Користувачі",
                    "separator": True,
                    "items": [
                        {
                            "title": "Користувачі",
                            "icon": "group",
                            "link": _admin_link("auth", "user"),
                        },
                    ],
                },
            ],
        },
    }
