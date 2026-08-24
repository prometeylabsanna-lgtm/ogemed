"""UNFOLD sidebar для OGEMED."""
from __future__ import annotations

from django.urls import reverse_lazy

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
                            "link": reverse_lazy("admin:core_sitesettings_changelist"),
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
                            "link": reverse_lazy("admin:cms_aboutcontent_changelist"),
                        },
                        {
                            "title": "CMS-сторінки",
                            "icon": "article",
                            "link": reverse_lazy("admin:cms_cmspage_changelist"),
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
                            "link": reverse_lazy("admin:catalog_product_changelist"),
                        },
                        {
                            "title": "Категорії",
                            "icon": "category",
                            "link": reverse_lazy("admin:catalog_category_changelist"),
                        },
                        {
                            "title": "Бренди",
                            "icon": "sell",
                            "link": reverse_lazy("admin:catalog_brand_changelist"),
                        },
                        {
                            "title": "Атрибути / фільтри",
                            "icon": "tune",
                            "link": reverse_lazy("admin:catalog_attribute_changelist"),
                        },
                        {
                            "title": "Варіанти",
                            "icon": "qr_code_2",
                            "link": reverse_lazy(
                                "admin:catalog_productvariant_changelist"
                            ),
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
                            "link": reverse_lazy("admin:orders_order_changelist"),
                        },
                        {
                            "title": "Ліди",
                            "icon": "support_agent",
                            "link": reverse_lazy("admin:cms_lead_changelist"),
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
                            "link": reverse_lazy("admin:auth_user_changelist"),
                        },
                    ],
                },
            ],
        },
    }
