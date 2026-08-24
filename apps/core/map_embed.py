"""Нормалізація посилання Google Maps / iframe → URL для src iframe на сайті."""
from __future__ import annotations

import re
import urllib.error
import urllib.parse
import urllib.request
from urllib.parse import parse_qs, unquote, urlparse

_IFRAME_SRC_RE = re.compile(
    r"""<iframe[^>]+src=["']([^"']+)["']""",
    re.IGNORECASE | re.DOTALL,
)
_COORDS_AT_RE = re.compile(r"@(-?\d+\.\d+)\s*,\s*(-?\d+\.\d+)")
_COORDS_Q_RE = re.compile(r"[?&]q=(-?\d+\.\d+)\s*,\s*(-?\d+\.\d+)")
_COORDS_PB_RE = re.compile(r"!2d(-?\d+\.\d+)!3d(-?\d+\.\d+)")
_SHORT_HOSTS = ("maps.app.goo.gl", "goo.gl", "g.co")


def _http_get_final_url(url: str, *, timeout: float = 8.0) -> str:
    req = urllib.request.Request(
        url,
        method="GET",
        headers={
            "User-Agent": (
                "Mozilla/5.0 (compatible; OGEMEDBot/1.0; +https://ogemed.ua)"
            ),
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.geturl() or url
    except (urllib.error.URLError, TimeoutError, ValueError, OSError):
        return url


def _embed_from_coords(lat: str, lng: str, *, zoom: int = 16) -> str:
    return (
        f"https://www.google.com/maps?q={lat},{lng}"
        f"&z={zoom}&hl=uk&output=embed"
    )


def _extract_coords(url: str) -> tuple[str, str] | None:
    for pattern in (_COORDS_AT_RE, _COORDS_Q_RE, _COORDS_PB_RE):
        match = pattern.search(url)
        if not match:
            continue
        a, b = match.group(1), match.group(2)
        # pb: !2dLNG!3dLAT
        if pattern is _COORDS_PB_RE:
            return b, a
        return a, b
    return None


def _to_embed_url(url: str) -> str:
    url = url.strip()
    if not url:
        return ""

    parsed = urlparse(url)
    host = (parsed.netloc or "").lower()

    if "/maps/embed" in parsed.path or "output=embed" in (parsed.query or ""):
        return url

    coords = _extract_coords(url)
    if coords:
        return _embed_from_coords(*coords)

    qs = parse_qs(parsed.query)
    if "q" in qs and qs["q"]:
        q = unquote(qs["q"][0])
        return (
            "https://www.google.com/maps?q="
            f"{urllib.parse.quote(q)}&z=16&hl=uk&output=embed"
        )

    if "google." in host and "/maps" in parsed.path:
        joiner = "&" if parsed.query else "?"
        return f"{url}{joiner}output=embed"

    return url


def normalize_map_embed(raw: str) -> str:
    """Приймає коротке посилання, повний URL або HTML iframe → URL для iframe src."""
    text = (raw or "").strip()
    if not text:
        return ""

    match = _IFRAME_SRC_RE.search(text)
    if match:
        text = match.group(1).strip()

    text = text.strip().strip('"').strip("'")

    parsed = urlparse(text)
    host = (parsed.netloc or "").lower()
    if any(h in host for h in _SHORT_HOSTS):
        text = _http_get_final_url(text)

    return _to_embed_url(text)
