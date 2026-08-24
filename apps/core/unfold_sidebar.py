"""UNFOLD sidebar для OGEMED.

Лінки — звичайні рядки (не reverse_lazy): Vercel серіалізує settings у JSON
і __str__ у Promise ламає AppRegistryNotReady.
"""
from __future__ import annotations

from apps.core.site_content_registry import build_content_sidebar_items


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
                            "link": "/admin/core/sitesettings/",
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
                            "link": "/admin/cms/aboutcontent/",
                        },
                        {
                            "title": "CMS-сторінки",
                            "icon": "article",
                            "link": "/admin/cms/cmspage/",
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
                            "link": "/admin/catalog/product/",
                        },
                        {
                            "title": "Категорії",
                            "icon": "category",
                            "link": "/admin/catalog/category/",
                        },
                        {
                            "title": "Бренди",
                            "icon": "sell",
                            "link": "/admin/catalog/brand/",
                        },
                        {
                            "title": "Атрибути / фільтри",
                            "icon": "tune",
                            "link": "/admin/catalog/attribute/",
                        },
                        {
                            "title": "Варіанти",
                            "icon": "qr_code_2",
                            "link": "/admin/catalog/productvariant/",
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
                            "link": "/admin/orders/order/",
                        },
                        {
                            "title": "Ліди",
                            "icon": "support_agent",
                            "link": "/admin/cms/lead/",
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
                            "link": "/admin/auth/user/",
                        },
                    ],
                },
            ],
        },
    }
