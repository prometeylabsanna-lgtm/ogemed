"""Створює .gz поруч зі static-файлами для nginx gzip_static."""

from __future__ import annotations

import gzip
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

_COMPRESS_SUFFIXES = {".css", ".js", ".svg", ".json", ".html", ".txt", ".xml", ".map"}


class Command(BaseCommand):
    help = "Стискає CSS/JS у STATIC_ROOT для gzip_static."

    def handle(self, *args, **options):
        root = Path(getattr(settings, "STATIC_ROOT", "") or "")
        if not root.is_dir():
            self.stdout.write("compress_static: STATIC_ROOT missing, skip")
            return
        written = 0
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in _COMPRESS_SUFFIXES:
                continue
            if path.name.endswith(".gz"):
                continue
            target = path.with_name(path.name + ".gz")
            data = path.read_bytes()
            if len(data) < 256:
                continue
            compressed = gzip.compress(data, compresslevel=9)
            if len(compressed) >= len(data):
                continue
            target.write_bytes(compressed)
            written += 1
        self.stdout.write(self.style.SUCCESS(f"compress_static: wrote {written} .gz files"))
