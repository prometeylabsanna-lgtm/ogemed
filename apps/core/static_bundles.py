"""Збірка CSS-бандлів з окремих source-файлів (без дублювання правил)."""

from __future__ import annotations

import re
from pathlib import Path, PurePosixPath

from django.conf import settings

# Порядок файлів фіксований — cascade залежить від нього.
BUNDLE_SOURCES: dict[str, tuple[str, ...]] = {
    "shell.css": (
        "css/base.css",
        "css/components/nav_arrow.css",
        "css/components/header.css",
        "css/components/mobile_nav.css",
        "css/components/breadcrumbs.css",
        "css/components/search_suggest.css",
        "css/components/footer.css",
    ),
    "overlays.css": (
        "css/components/cart.css",
        "css/components/cart_popup.css",
        "css/components/callback_modal.css",
        "css/components/form_validation.css",
        "css/components/cookie_banner.css",
    ),
    "home.css": (
        "css/components/product_card.css",
        "css/components/product_grid.css",
        "css/components/product_slider.css",
        "css/components/home.css",
        "css/components/slider_bars.css",
        "css/components/brand_showcase.css",
    ),
    "catalog.css": (
        "css/components/product_card.css",
        "css/components/product_grid.css",
        "css/components/catalog.css",
        "css/components/catalog_brands.css",
        "css/components/catalog_toolbar.css",
        "css/components/catalog_more.css",
        "css/components/label_icons.css",
    ),
    "catalog_search.css": (
        "css/components/product_card.css",
        "css/components/product_grid.css",
        "css/components/catalog.css",
        "css/components/catalog_more.css",
    ),
    "brand_detail.css": (
        "css/components/product_card.css",
        "css/components/product_grid.css",
        "css/components/catalog.css",
        "css/components/catalog_toolbar.css",
        "css/components/catalog_more.css",
        "css/components/brand_tiles.css",
    ),
    "brands.css": ("css/components/brand_tiles.css",),
    "pdp.css": (
        "css/components/label_icons.css",
        "css/components/pdp.css",
        "css/components/pdp_variants.css",
        "css/components/pdp_zoom.css",
        "css/components/slider_bars.css",
    ),
    "about.css": (
        "css/components/about.css",
        "css/components/about_history.css",
        "css/components/about_philosophy.css",
    ),
    "auth.css": ("css/components/auth.css",),
    "cabinet.css": ("css/components/cabinet.css",),
    "cabinet_order.css": (
        "css/components/cabinet.css",
        "css/components/thankyou_fop.css",
    ),
    "cart_page.css": ("css/components/cart_page.css",),
    "checkout.css": (
        "css/components/checkout.css",
        "css/components/checkout_acc.css",
        "css/components/checkout_payment.css",
    ),
    "thankyou.css": (
        "css/components/checkout_thankyou.css",
        "css/components/thankyou_fop.css",
    ),
    "contacts.css": ("css/components/contacts.css",),
    "info_page.css": (
        "css/components/info-page.css",
        "css/components/info_page_cta_sheet.css",
    ),
    "info_page_shipping.css": (
        "css/components/info-page.css",
        "css/components/info_page_steps.css",
        "css/components/info_page_cta_sheet.css",
    ),
    "error_page.css": ("css/components/error_page.css",),
}

_URL_RE = re.compile(
    r"""url\(\s*(['"]?)([^)'"]+)\1\s*\)""",
    re.IGNORECASE,
)


def _static_root() -> Path:
    return Path(settings.BASE_DIR) / "static"


def _rewrite_urls(css_text: str, source_rel: str, out_rel_dir: str) -> str:
    """Переписати відносні url() з позиції source у позицію бандла."""
    source_dir = PurePosixPath(source_rel).parent
    out_dir = PurePosixPath(out_rel_dir)

    def repl(match: re.Match[str]) -> str:
        quote, raw = match.group(1), match.group(2).strip()
        # data:/http(s)/absolute/fragment (#id або %23id всередині SVG data-URI)
        if (
            not raw
            or raw.startswith(("data:", "http://", "https://", "/", "#", "%23"))
        ):
            return match.group(0)
        resolved = (source_dir / raw).as_posix()
        # normalize .. segments
        parts: list[str] = []
        for part in resolved.split("/"):
            if part == "..":
                if parts:
                    parts.pop()
            elif part and part != ".":
                parts.append(part)
        abs_posix = "/".join(parts)
        rel = PurePosixPath(os_path_rel(out_dir.as_posix(), abs_posix))
        q = quote or ""
        return f"url({q}{rel.as_posix()}{q})"

    return _URL_RE.sub(repl, css_text)


def os_path_rel(from_dir: str, to_file: str) -> str:
    """Відносний шлях від каталогу from_dir до to_file (posix)."""
    from_parts = [p for p in from_dir.split("/") if p]
    to_parts = [p for p in to_file.split("/") if p]
    i = 0
    while i < len(from_parts) and i < len(to_parts) and from_parts[i] == to_parts[i]:
        i += 1
    ups = [".."] * (len(from_parts) - i)
    return "/".join(ups + to_parts[i:])


def build_bundles(*, quiet: bool = False) -> list[Path]:
    """Зібрати бандли в static/css/bundles/. Повертає список записаних шляхів."""
    static_root = _static_root()
    out_dir = static_root / "css" / "bundles"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_rel_dir = "css/bundles"
    written: list[Path] = []

    for bundle_name, sources in BUNDLE_SOURCES.items():
        parts: list[str] = [
            f"/* AUTO-GENERATED: {bundle_name} — do not edit; run build_static_bundles */\n"
        ]
        for rel in sources:
            path = static_root / rel
            if not path.is_file():
                raise FileNotFoundError(f"Missing CSS source for bundle {bundle_name}: {path}")
            raw = path.read_text(encoding="utf-8")
            rewritten = _rewrite_urls(raw, rel, out_rel_dir)
            parts.append(f"\n/* === {rel} === */\n")
            parts.append(rewritten)
            if not parts[-1].endswith("\n"):
                parts.append("\n")
        out_path = out_dir / bundle_name
        out_path.write_text("".join(parts), encoding="utf-8")
        written.append(out_path)
        if not quiet:
            print(f"  wrote {out_path.relative_to(static_root)} ({len(sources)} files)")

    return written
