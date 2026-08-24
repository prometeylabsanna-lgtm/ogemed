"""Registry CMS-секцій для Unfold sidebar."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterator

from apps.core.block_defaults import BLOCK_FIELD_LABELS


@dataclass(frozen=True)
class FieldGroup:
    title: str
    block_keys: tuple[str, ...]


@dataclass(frozen=True)
class ContentSection:
    slug: str
    page_slug: str
    title: str
    blocks: tuple[tuple[str, str], ...]
    sidebar_title: str = ""
    sidebar_icon: str = "edit_note"
    preview_url: str = "/"
    description: str = ""
    visibility_key: str = ""
    field_groups: tuple[FieldGroup, ...] = field(default_factory=tuple)
    admin_model_name: str = ""


CONTENT_SECTIONS: tuple[ContentSection, ...] = (
    ContentSection(
        slug="hero",
        page_slug="home",
        title="Головний банер",
        sidebar_title="Головна — банер",
        sidebar_icon="image",
        preview_url="/",
        admin_model_name="homeherosettings",
        description=(
            "Текст, який показується на головній, коли немає жодного активного "
            "слайда в каруселі. Слайди налаштовуються нижче на цій сторінці."
        ),
        visibility_key="hero_section_visible",
        blocks=(
            ("home", "hero_fallback_title"),
            ("home", "hero_fallback_subtitle"),
        ),
        field_groups=(
            FieldGroup(
                "Текст, якщо немає слайдів",
                ("hero_fallback_title", "hero_fallback_subtitle"),
            ),
        ),
    ),
    ContentSection(
        slug="products",
        page_slug="home",
        title="Новинки та хіти",
        sidebar_title="Головна — Товари",
        sidebar_icon="inventory_2",
        preview_url="/",
        admin_model_name="homeproductssettings",
        visibility_key="products_section_visible",
        description="Товари з прапорцями «Новинка» / «Хіт» — у Каталозі.",
        blocks=(
            ("home", "products_new_title"),
            ("home", "products_hits_title"),
        ),
        field_groups=(
            FieldGroup("Заголовки", ("products_new_title", "products_hits_title")),
        ),
    ),
    ContentSection(
        slug="care",
        page_slug="home",
        title="Підбір догляду",
        sidebar_title="Головна — Підбір",
        sidebar_icon="spa",
        preview_url="/",
        admin_model_name="homecaresettings",
        visibility_key="care_section_visible",
        blocks=(
            ("home", "care_section_title"),
            ("home", "care_section_text"),
            ("home", "care_cta_label"),
            ("home", "care_cta_url"),
            ("home", "care_section_image"),
        ),
        field_groups=(
            FieldGroup(
                "Контент",
                ("care_section_title", "care_section_text", "care_cta_label", "care_cta_url"),
            ),
            FieldGroup("Фон", ("care_section_image",)),
        ),
    ),
    ContentSection(
        slug="brands",
        page_slug="home",
        title="Вітрина брендів",
        sidebar_title="Головна — Бренди",
        sidebar_icon="sell",
        preview_url="/",
        admin_model_name="homebrandssettings",
        visibility_key="brands_section_visible",
        blocks=(("home", "brands_section_title"),),
        field_groups=(FieldGroup("Заголовок", ("brands_section_title",)),),
    ),
    ContentSection(
        slug="intro",
        page_slug="contacts",
        title="Intro контактів",
        sidebar_title="Контакти — Intro",
        sidebar_icon="call",
        preview_url="/kontakty/",
        admin_model_name="contactsintrosettings",
        description="Телефон, email, адреса, карта — у «Налаштування сайту».",
        blocks=(
            ("contacts", "intro_title"),
            ("contacts", "intro_text"),
            ("contacts", "cta_label"),
        ),
        field_groups=(
            FieldGroup("Текст", ("intro_title", "intro_text", "cta_label")),
        ),
    ),
    ContentSection(
        slug="header",
        page_slug="site",
        title="Шапка",
        sidebar_title="Шапка сайту",
        sidebar_icon="web",
        preview_url="/",
        admin_model_name="siteheadersettings",
        description=(
            "Логотип і телефон — ті самі значення, що в «Налаштування сайту». "
            "Placeholder пошуку можна задати окремо для UA/RU."
        ),
        blocks=(("site", "header_search_placeholder"),),
        field_groups=(FieldGroup("Пошук", ("header_search_placeholder",)),),
    ),
    ContentSection(
        slug="footer",
        page_slug="site",
        title="Підвал",
        sidebar_title="Підвал сайту",
        sidebar_icon="dock_to_bottom",
        preview_url="/",
        admin_model_name="sitefootersettings",
        blocks=(
            ("site", "footer_about_text"),
            ("site", "footer_copyright"),
        ),
        field_groups=(
            FieldGroup("Тексти", ("footer_about_text", "footer_copyright")),
        ),
    ),
)

SECTION_BY_ADMIN_MODEL = {
    section.admin_model_name: section for section in CONTENT_SECTIONS
}


def get_block_field_label(page: str, key: str) -> str:
    return BLOCK_FIELD_LABELS.get((page, key), key.replace("_", " ").capitalize())


def get_section(page_slug: str, section_slug: str) -> ContentSection:
    for section in CONTENT_SECTIONS:
        if section.page_slug == page_slug and section.slug == section_slug:
            return section
    raise KeyError(f"Section {section_slug!r} not found on page {page_slug!r}")


def iter_section_blocks(section: ContentSection) -> Iterator[tuple[str, str]]:
    yield from section.blocks
    if not section.visibility_key:
        return
    page = section.blocks[0][0] if section.blocks else section.page_slug
    yield page, section.visibility_key


def build_content_sidebar_items(*, admin_url: str = "ogm8k2x9p4qh7n") -> list[dict]:
    prefix = (admin_url or "ogm8k2x9p4qh7n").strip("/")
    return [
        {
            "title": section.sidebar_title or section.title,
            "icon": section.sidebar_icon,
            "link": f"/{prefix}/core/{section.admin_model_name}/",
        }
        for section in CONTENT_SECTIONS
    ]
