"""Очищення HTML з адмінки: звичайний текст без тегів, richtext — лише безпечні."""
from __future__ import annotations

import re
from html import unescape
from html.parser import HTMLParser

from django.utils.html import escape, strip_tags
from django.utils.safestring import SafeString, mark_safe

RICH_FIELD_NAMES = frozenset(
    {
        "body",
        "body_uk",
        "body_ru",
        "description_uk",
        "description_ru",
    }
)
RICH_FIELD_BASES = frozenset({"body", "description"})

ALLOWED_TAGS = frozenset(
    {"p", "br", "strong", "b", "em", "i", "u", "ul", "ol", "li", "a", "span", "h2", "h3", "h4"}
)
VOID_TAGS = frozenset({"br"})
ALLOWED_ATTRS = {
    "a": frozenset({"href", "title", "rel", "target"}),
    "span": frozenset({"style"}),
}

TINYMCE_VALID_ELEMENTS = (
    "p,br,strong/b,em/i,u,ul,ol,li,a[href|target|rel|title],span[style],h2,h3,h4"
)

_BR_RE = re.compile(r"(?i)<br\s*/?>")
_BLOCK_END_RE = re.compile(r"(?i)</(p|div|h[1-6]|li|tr)\s*>")
_STYLE_OK = re.compile(
    r"^\s*(?:color|font-size)\s*:\s*[^;]+(?:\s*;\s*(?:color|font-size)\s*:\s*[^;]+)*\s*;?\s*$",
    re.I,
)
_STYLE_DANGER = re.compile(r"expression|url\s*\(|javascript:|@import|behavior", re.I)


def is_rich_field_name(name: str) -> bool:
    return name in RICH_FIELD_NAMES


def is_rich_field_base(field_base: str) -> bool:
    return field_base in RICH_FIELD_BASES


def plain_text(value: str | None, *, single_line: bool = False) -> str:
    """Прибрати всі HTML-теги; <br>/</p> → перенос (або пробіл у single_line)."""
    if not value:
        return ""
    if isinstance(value, SafeString) and "<" not in value:
        return str(value)
    text = unescape(str(value))
    text = _BR_RE.sub("\n", text)
    text = _BLOCK_END_RE.sub("\n", text)
    text = strip_tags(text)
    text = unescape(text).replace("\xa0", " ")
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    if single_line:
        text = re.sub(r"\s+", " ", text)
    return text.strip()


def _safe_href(value: str) -> str:
    raw = (value or "").strip()
    low = raw.lower()
    if "javascript:" in low or "data:" in low or "vbscript:" in low:
        return ""
    if raw.startswith(("https://", "http://", "/", "mailto:", "tel:", "#")):
        return raw
    return ""


def _safe_style(value: str) -> str:
    raw = (value or "").strip()
    if not raw or _STYLE_DANGER.search(raw):
        return ""
    if not _STYLE_OK.match(raw):
        return ""
    return raw


class _RichSanitizer(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._out: list[str] = []
        self._stack: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag not in ALLOWED_TAGS:
            return
        chunks: list[str] = []
        allowed = ALLOWED_ATTRS.get(tag, frozenset())
        for name, val in attrs:
            name = name.lower()
            if name not in allowed:
                continue
            raw = val or ""
            if name == "href":
                raw = _safe_href(raw)
                if not raw:
                    continue
            elif name == "style":
                raw = _safe_style(raw)
                if not raw:
                    continue
            elif name == "target":
                if raw not in {"_blank", "_self"}:
                    continue
                chunks.append('rel="noopener noreferrer"')
            chunks.append(f'{name}="{escape(raw)}"')
        extra = f" {' '.join(chunks)}" if chunks else ""
        if tag in VOID_TAGS:
            self._out.append(f"<{tag}{extra}>")
            return
        self._stack.append(tag)
        self._out.append(f"<{tag}{extra}>")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag not in ALLOWED_TAGS or tag in VOID_TAGS:
            return
        if tag not in self._stack:
            return
        while self._stack:
            last = self._stack.pop()
            self._out.append(f"</{last}>")
            if last == tag:
                break

    def handle_data(self, data: str) -> None:
        self._out.append(escape(data))

    def get_html(self) -> str:
        while self._stack:
            self._out.append(f"</{self._stack.pop()}>")
        return "".join(self._out).strip()


def sanitize_richtext(value: str | None) -> str:
    """Allowlist HTML для TinyMCE; скрипти й зайві теги викидаються."""
    if not value:
        return ""
    parser = _RichSanitizer()
    parser.feed(str(value))
    parser.close()
    return parser.get_html()


def richtext_html(value: str | None) -> SafeString:
    return mark_safe(sanitize_richtext(value))


def clean_field_value(field_name: str, value: str, *, single_line: bool) -> str:
    if is_rich_field_name(field_name):
        return sanitize_richtext(value)
    return plain_text(value, single_line=single_line)
