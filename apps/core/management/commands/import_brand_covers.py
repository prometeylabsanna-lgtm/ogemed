"""Імпорт фото брендів для плиток каталогу (cover_image).

Вітрину на головній тримає окреме поле showcase_image (PNG без фону) — команда
його не змінює.

Ім'я файлу без розширення = slug бренду (наприклад yellow-rose.jpg).
Фото доводиться до 4:5 без обрізання: вільне місце заливається кольором рамки
самого знімка, тому на світлих і темних фонах немає видимих смуг.

    python3 manage.py import_brand_covers --src media/brands/sources
    python3 manage.py import_brand_covers --src <dir> --force
"""
from __future__ import annotations

from io import BytesIO
from pathlib import Path
from statistics import median

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from PIL import Image

from apps.catalog.models import Brand

SUPPORTED_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".avif"}
TARGET_RATIO = (4, 5)
TARGET_WIDTH = 900
WEBP_QUALITY = 86


def _border_color(image: Image.Image) -> tuple[int, int, int]:
    """Медіанний колір рамки — ним заливається додане поле."""
    width, height = image.size
    pixels = image.load()
    samples = [pixels[x, 0] for x in range(0, width, max(1, width // 64))]
    samples += [pixels[x, height - 1] for x in range(0, width, max(1, width // 64))]
    samples += [pixels[0, y] for y in range(0, height, max(1, height // 64))]
    samples += [pixels[width - 1, y] for y in range(0, height, max(1, height // 64))]
    return tuple(int(median(channel[i] for channel in samples)) for i in range(3))


def _to_cover(path: Path) -> bytes:
    with Image.open(path) as raw:
        raw.load()
        source = raw.convert("RGB") if raw.mode != "RGBA" else raw
        background = _border_color(source.convert("RGB"))

        width, height = source.size
        ratio_w, ratio_h = TARGET_RATIO
        if width * ratio_h > height * ratio_w:
            canvas_size = (width, round(width * ratio_h / ratio_w))
        else:
            canvas_size = (round(height * ratio_w / ratio_h), height)

        canvas = Image.new("RGB", canvas_size, background)
        offset = (
            (canvas_size[0] - width) // 2,
            (canvas_size[1] - height) // 2,
        )
        if source.mode == "RGBA":
            canvas.paste(source, offset, source)
        else:
            canvas.paste(source, offset)

        if canvas.width > TARGET_WIDTH:
            target_height = round(canvas.height * TARGET_WIDTH / canvas.width)
            canvas = canvas.resize((TARGET_WIDTH, target_height), Image.LANCZOS)

        buffer = BytesIO()
        canvas.save(buffer, format="WEBP", quality=WEBP_QUALITY, method=6)
        return buffer.getvalue()


class Command(BaseCommand):
    help = "Імпорт cover_image брендів із теки (ім'я файлу = slug бренду). Вітрину на головній не чіпає."

    def add_arguments(self, parser):
        parser.add_argument("--src", required=True, help="Тека з фото брендів")
        parser.add_argument(
            "--force",
            action="store_true",
            help="Перезаписати фото, які вже стоять у брендів",
        )

    def handle(self, *args, **options):
        src = Path(options["src"]).expanduser()
        if not src.is_dir():
            raise CommandError(f"Немає теки: {src}")

        imported = skipped = 0
        for path in sorted(src.iterdir()):
            if path.suffix.lower() not in SUPPORTED_SUFFIXES:
                continue

            brand = Brand.objects.filter(slug=path.stem).first()
            if brand is None:
                self.stdout.write(self.style.WARNING(f"× бренд {path.stem} не знайдено"))
                skipped += 1
                continue

            if brand.cover_image and not options["force"]:
                self.stdout.write(f"· {brand.slug}: фото вже є (--force щоб замінити)")
                skipped += 1
                continue

            brand.cover_image.save(
                f"{brand.slug}.webp", ContentFile(_to_cover(path)), save=True
            )
            imported += 1
            self.stdout.write(self.style.SUCCESS(f"✓ {brand.slug} → {brand.cover_image.name}"))

        self.stdout.write(
            self.style.SUCCESS(f"Готово: {imported} імпортовано, {skipped} пропущено.")
        )
