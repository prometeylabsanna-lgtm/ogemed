"""Оптимізація завантажених зображень: WebP, ресайз, EXIF, SVG-санітизація."""

from __future__ import annotations

import io
import re
import uuid
from pathlib import Path

from django.core.files.base import ContentFile
from django.utils.text import slugify
from PIL import Image, ImageOps

WEBP_QUALITY = 83
THUMB_MAX_SIDE = 240

MAX_SIDE_PRODUCT = 2048
MAX_SIDE_HERO = 2560
MAX_SIDE_LOGO = 1024
MAX_SIDE_DEFAULT = 2048

_SVG_SCRIPT_RE = re.compile(r"<script\b[^>]*>.*?</script>", re.IGNORECASE | re.DOTALL)
_SVG_FOREIGN_RE = re.compile(
    r"<foreignObject\b[^>]*>.*?</foreignObject>", re.IGNORECASE | re.DOTALL
)
_SVG_EVENT_RE = re.compile(
    r"\son\w+\s*=\s*(\"[^\"]*\"|'[^']*'|[^\s>]+)", re.IGNORECASE
)
_SVG_JS_RE = re.compile(r"javascript\s*:", re.IGNORECASE)
_SVG_DANGEROUS_TAG_RE = re.compile(
    r"</?(?:iframe|embed|object|link|meta)\b[^>]*>", re.IGNORECASE
)


def is_svg_upload(uploaded) -> bool:
    name = (getattr(uploaded, "name", "") or "").lower()
    content_type = (getattr(uploaded, "content_type", "") or "").lower()
    if name.endswith(".svg") or "svg" in content_type:
        return True
    try:
        pos = uploaded.tell()
        head = uploaded.read(256)
        uploaded.seek(pos)
    except Exception:
        return False
    if not head:
        return False
    snippet = head.lstrip()[:200].lower()
    return snippet.startswith(b"<?xml") or snippet.startswith(b"<svg")


def sanitize_svg(data: bytes) -> bytes:
    text = data.decode("utf-8", errors="replace")
    text = _SVG_SCRIPT_RE.sub("", text)
    text = _SVG_FOREIGN_RE.sub("", text)
    text = _SVG_DANGEROUS_TAG_RE.sub("", text)
    text = _SVG_EVENT_RE.sub("", text)
    text = _SVG_JS_RE.sub("", text)
    return text.encode("utf-8")


def safe_media_filename(original_name: str, extension: str) -> str:
    stem = Path(original_name or "img").stem
    slug = slugify(stem, allow_unicode=False)[:40].strip("-") or "img"
    ext = extension if extension.startswith(".") else f".{extension}"
    return f"{slug}-{uuid.uuid4().hex[:12]}{ext}"


def thumb_storage_name(name: str) -> str:
    if not name:
        return ""
    path = Path(name)
    return str(path.with_name(f"{path.stem}_thumb.webp"))


def thumb_url(field_file) -> str:
    """URL мініатюри, якщо є; інакше оригінал."""
    if not field_file:
        return ""
    try:
        name = field_file.name
    except Exception:
        return ""
    if not name:
        return ""
    if str(name).lower().endswith(".svg"):
        return field_file.url
    thumb = thumb_storage_name(name)
    storage = field_file.storage
    try:
        if storage.exists(thumb):
            return storage.url(thumb)
    except Exception:
        pass
    try:
        return field_file.url
    except Exception:
        return ""


def _prepare_mode(img: Image.Image) -> Image.Image:
    if img.mode == "CMYK":
        return img.convert("RGB")
    if img.mode == "P":
        return img.convert("RGBA") if "transparency" in img.info else img.convert("RGB")
    if img.mode == "LA":
        return img.convert("RGBA")
    if img.mode in {"RGBA", "RGB"}:
        return img
    if img.mode == "L":
        return img.convert("RGB")
    return img.convert("RGB")


def _fit_max_side(img: Image.Image, max_side: int) -> Image.Image:
    if max_side <= 0:
        return img
    width, height = img.size
    longest = max(width, height)
    if longest <= max_side:
        return img
    scale = max_side / float(longest)
    new_size = (max(1, int(width * scale)), max(1, int(height * scale)))
    return img.resize(new_size, Image.Resampling.LANCZOS)


def _encode_webp(img: Image.Image, quality: int = WEBP_QUALITY) -> bytes:
    buffer = io.BytesIO()
    params = {
        "format": "WEBP",
        "quality": quality,
        "method": 6,
    }
    if img.mode in {"RGBA", "LA"}:
        params["exact"] = True
    img.save(buffer, **params)
    return buffer.getvalue()


def raster_to_webp(
    source,
    *,
    max_side: int = MAX_SIDE_DEFAULT,
    quality: int = WEBP_QUALITY,
    thumb_side: int = THUMB_MAX_SIDE,
) -> tuple[bytes, bytes | None, tuple[int, int]]:
    """
    Повертає (webp_bytes, thumb_bytes|None, (width, height)).
    Автоповорот EXIF, без метаданих, ресайз лише вниз.
    """
    if hasattr(source, "seek"):
        source.seek(0)
    with Image.open(source) as original:
        img = ImageOps.exif_transpose(original)
        img.load()
        img = _prepare_mode(img)
        img = _fit_max_side(img, max_side)
        # Новий обʼєкт без EXIF/ICC профілів
        clean = img.copy()
        if "exif" in clean.info:
            clean.info.pop("exif", None)
        if "icc_profile" in clean.info:
            clean.info.pop("icc_profile", None)
        size = clean.size
        webp_bytes = _encode_webp(clean, quality=quality)

        thumb_bytes = None
        if thumb_side > 0:
            thumb = _fit_max_side(clean, thumb_side)
            thumb_bytes = _encode_webp(thumb, quality=min(quality, 80))

    return webp_bytes, thumb_bytes, size


def process_upload(
    uploaded,
    *,
    max_side: int = MAX_SIDE_DEFAULT,
    quality: int = WEBP_QUALITY,
    generate_thumb: bool = True,
    allow_svg: bool = False,
    original_name: str | None = None,
) -> tuple[ContentFile, ContentFile | None]:
    """
    Обробити UploadedFile / file-like.
    Повертає (main ContentFile, thumb ContentFile|None).
    """
    name = original_name or getattr(uploaded, "name", "") or "image"
    if is_svg_upload(uploaded):
        if not allow_svg:
            raise ValueError("SVG не дозволено для цього поля")
        if hasattr(uploaded, "seek"):
            uploaded.seek(0)
        raw = uploaded.read()
        cleaned = sanitize_svg(raw)
        main = ContentFile(cleaned, name=safe_media_filename(name, ".svg"))
        return main, None

    thumb_side = THUMB_MAX_SIDE if generate_thumb else 0
    webp_bytes, thumb_bytes, _size = raster_to_webp(
        uploaded,
        max_side=max_side,
        quality=quality,
        thumb_side=thumb_side,
    )
    main = ContentFile(webp_bytes, name=safe_media_filename(name, ".webp"))
    thumb = None
    if thumb_bytes:
        thumb = ContentFile(
            thumb_bytes,
            name=thumb_storage_name(main.name),
        )
    return main, thumb
