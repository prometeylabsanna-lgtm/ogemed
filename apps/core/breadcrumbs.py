"""Breadcrumb helpers for public pages."""
from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse

from django.urls import reverse
from django.utils.translation import gettext as _


@dataclass(frozen=True)
class BreadcrumbItem:
    label: str
    url: str | None = None

    @property
    def is_current(self) -> bool:
        return self.url is None


def build_breadcrumbs(
    request,
    *items: tuple[str, str | None] | BreadcrumbItem,
) -> list[BreadcrumbItem]:
    """Крихти з «Головна»; останній елемент — поточна сторінка без посилання."""
    crumbs: list[BreadcrumbItem] = [
        BreadcrumbItem(label=_("Головна"), url=reverse("core:home")),
    ]

    for item in items:
        if isinstance(item, BreadcrumbItem):
            crumbs.append(item)
        else:
            label, url = item
            crumbs.append(BreadcrumbItem(label=label, url=url))

    if not crumbs:
        return crumbs

    last = crumbs[-1]
    if last.url is not None:
        crumbs[-1] = BreadcrumbItem(label=last.label, url=None)

    if len(crumbs) == 2 and crumbs[0].label == crumbs[1].label:
        return [BreadcrumbItem(label=crumbs[0].label, url=None)]

    return crumbs


def translate_path_for_language(path: str, language: str) -> str:
    """Еквівалентний шлях для перемикача мови (uk без префікса, ru — /ru/)."""
    parsed = urlparse(path)
    clean = parsed.path or "/"
    for code in ("uk", "ru"):
        prefix = f"/{code}/"
        if clean.startswith(prefix):
            clean = "/" + clean[len(prefix) :]
            break
        if clean == f"/{code}":
            clean = "/"
            break

    if language == "uk":
        new_path = clean
    else:
        new_path = f"/{language}{clean}" if clean != "/" else f"/{language}/"

    if parsed.query:
        new_path = f"{new_path}?{parsed.query}"
    return new_path


def language_switch_urls(request) -> dict[str, str]:
    path = request.get_full_path()
    return {
        "uk": translate_path_for_language(path, "uk"),
        "ru": translate_path_for_language(path, "ru"),
    }
