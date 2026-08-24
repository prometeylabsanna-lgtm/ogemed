"""UNFOLD sidebar + тема OGEMED (кольори сайту, favicon).

Лінки — рядки (не reverse_lazy): Vercel серіалізує settings у JSON.
Префікс admin_url передавати явно з settings.base.
"""
from __future__ import annotations

from apps.core.site_content_registry import build_content_sidebar_items

# Палітра з static/css/base.css — Unfold чекає "R G B" або "#hex"
_OGEMED_PRIMARY = {
    "50": "253 248 247",
    "100": "251 238 236",
    "200": "246 220 216",
    "300": "239 195 189",
    "400": "227 161 153",
    "500": "206 138 131",  # --color-accent
    "600": "178 104 96",
    "700": "140 79 73",  # --color-accent-700
    "800": "100 56 53",
    "900": "64 35 34",
    "950": "42 22 21",
}

_OGEMED_BASE = {
    "50": "252 250 247",
    "100": "249 244 237",  # --color-neutral-100 / cream
    "200": "238 231 219",
    "300": "220 211 196",
    "400": "192 182 165",
    "500": "161 151 134",
    "600": "130 121 106",
    "700": "100 92 80",
    "800": "71 66 56",
    "900": "46 43 37",
    "950": "32 30 29",  # --color-text
}


def _admin_link(prefix: str, *parts: str) -> str:
    base = (prefix or "ogm8k2x9p4qh7n").strip("/")
    path = "/".join(p.strip("/") for p in parts if p)
    return f"/{base}/{path}/" if path else f"/{base}/"


def _admin_link_query(prefix: str, *parts: str, query: str = "") -> str:
    url = _admin_link(prefix, *parts)
    return f"{url}?{query}" if query else url


_LEGAL_PAGES = (
    ("shipping", "Доставка і оплата", "local_shipping"),
    ("returns", "Повернення", "undo"),
    ("privacy", "Конфіденційність", "policy"),
    ("offer", "Оферта", "gavel"),
)


def _legal_page_sidebar_items(prefix: str) -> list[dict]:
    return [
        {
            "title": title,
            "icon": icon,
            "link": _admin_link_query(
                prefix,
                "cms",
                "infopagesection",
                query=f"page_key__exact={key}",
            ),
        }
        for key, title, icon in _LEGAL_PAGES
    ]


def build_unfold_config(*, admin_url: str = "ogm8k2x9p4qh7n") -> dict:
    prefix = (admin_url or "ogm8k2x9p4qh7n").strip("/")
    return {
        "SITE_TITLE": "OGEMED Admin",
        "SITE_HEADER": "",
        "SITE_SUBHEADER": "",
        "SITE_URL": "/",
        "THEME": "light",
        "SHOW_HISTORY": True,
        "SHOW_VIEW_ON_SITE": True,
        "SITE_ICON": {
            "light": "/static/img/logo.png",
            "dark": "/static/img/logo.png",
        },
        "SITE_FAVICONS": [
            {
                "rel": "icon",
                "sizes": "any",
                "type": "image/x-icon",
                "href": "/static/img/favicon.ico",
            },
            {
                "rel": "icon",
                "sizes": "32x32",
                "type": "image/png",
                "href": "/static/img/favicon-32.png",
            },
            {
                "rel": "apple-touch-icon",
                "sizes": "180x180",
                "type": "image/png",
                "href": "/static/img/apple-touch-icon.png",
            },
        ],
        "COLORS": {
            "primary": _OGEMED_PRIMARY,
            "base": _OGEMED_BASE,
            "font": {
                "subtle-light": "var(--color-base-500)",
                "subtle-dark": "var(--color-base-400)",
                "default-light": "var(--color-base-700)",
                "default-dark": "var(--color-base-300)",
                "important-light": "var(--color-base-950)",
                "important-dark": "var(--color-base-100)",
            },
        },
        "STYLES": [
            "/static/css/admin/ogemed_theme.css",
        ],
        "SCRIPTS": [
            "/static/js/admin/theme-init.js",
            "/static/js/admin/filters.js",
        ],
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
                            "link": _admin_link(prefix, "core", "sitesettings"),
                        },
                    ],
                },
                {
                    "title": "Вміст сторінок",
                    "separator": True,
                    "collapsible": True,
                    "items": build_content_sidebar_items(admin_url=prefix),
                },
                {
                    "title": "Про нас (детально)",
                    "separator": True,
                    "items": [
                        {
                            "title": "Контент «Про нас»",
                            "icon": "info",
                            "link": _admin_link(prefix, "cms", "aboutcontent"),
                        },
                        {
                            "title": "CMS-сторінки",
                            "icon": "article",
                            "link": _admin_link(prefix, "cms", "cmspage"),
                        },
                    ],
                },
                {
                    "title": "Юридичні сторінки",
                    "separator": True,
                    "collapsible": True,
                    "items": [
                        *_legal_page_sidebar_items(prefix),
                        {
                            "title": "CTA / замітки (усі)",
                            "icon": "notes",
                            "link": _admin_link(prefix, "cms", "infopagemeta"),
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
                            "link": _admin_link(prefix, "catalog", "product"),
                        },
                        {
                            "title": "Категорії",
                            "icon": "category",
                            "link": _admin_link(prefix, "catalog", "category"),
                        },
                        {
                            "title": "Бренди",
                            "icon": "sell",
                            "link": _admin_link(prefix, "catalog", "brand"),
                        },
                        {
                            "title": "Атрибути / фільтри",
                            "icon": "tune",
                            "link": _admin_link(prefix, "catalog", "attribute"),
                        },
                        {
                            "title": "Іконки міток",
                            "icon": "loyalty",
                            "link": _admin_link(prefix, "catalog", "labelicon"),
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
                            "link": _admin_link(prefix, "orders", "order"),
                        },
                        {
                            "title": "Ліди",
                            "icon": "support_agent",
                            "link": _admin_link(prefix, "cms", "lead"),
                        },
                    ],
                },
                {
                    "title": "Недавні дії",
                    "separator": True,
                    "items": [
                        {
                            "title": "Недавні дії",
                            "icon": "history",
                            "link": _admin_link(prefix, "admin", "logentry"),
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
                            "link": _admin_link(prefix, "auth", "user"),
                        },
                    ],
                },
            ],
        },
    }
