"""Реєстр юридичних / інфо-сторінок для єдиного адмін-редактора."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LegalPageDef:
    key: str
    title: str
    icon: str
    preview_path: str
    slug_default: str
    model_name: str
    has_about: bool = False
    has_sections: bool = False
    has_meta: bool = False
    has_fop: bool = False


LEGAL_PAGES: tuple[LegalPageDef, ...] = (
    LegalPageDef(
        key="about",
        title="Про нас",
        icon="info",
        preview_path="/pro-nas/",
        slug_default="pro-nas",
        model_name="legalaboutpage",
        has_about=True,
    ),
    LegalPageDef(
        key="contacts",
        title="Контакти",
        icon="call",
        preview_path="/kontakty/",
        slug_default="kontakty",
        model_name="legalcontactspage",
    ),
    LegalPageDef(
        key="shipping",
        title="Доставка і оплата",
        icon="local_shipping",
        preview_path="/dostavka-i-oplata/",
        slug_default="dostavka-i-oplata",
        model_name="legalshippingpage",
        has_sections=True,
        has_meta=True,
        has_fop=True,
    ),
    LegalPageDef(
        key="returns",
        title="Повернення",
        icon="undo",
        preview_path="/povernennya/",
        slug_default="povernennya",
        model_name="legalreturnspage",
        has_sections=True,
        has_meta=True,
    ),
    LegalPageDef(
        key="privacy",
        title="Конфіденційність",
        icon="policy",
        preview_path="/polityka-konfidentsiynosti/",
        slug_default="polityka-konfidentsiynosti",
        model_name="legalprivacypage",
        has_sections=True,
        has_meta=True,
    ),
    LegalPageDef(
        key="offer",
        title="Оферта",
        icon="gavel",
        preview_path="/publichna-oferta/",
        slug_default="publichna-oferta",
        model_name="legalofferpage",
        has_sections=True,
        has_meta=True,
        has_fop=True,
    ),
)

LEGAL_PAGES_BY_KEY = {p.key: p for p in LEGAL_PAGES}
LEGAL_PAGES_BY_MODEL = {p.model_name: p for p in LEGAL_PAGES}


def get_legal_page(key: str) -> LegalPageDef:
    try:
        return LEGAL_PAGES_BY_KEY[key]
    except KeyError as exc:
        raise KeyError(key) from exc
