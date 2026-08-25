"""Зібрати static/css/bundles/*.css з окремих source-файлів."""

from django.core.management.base import BaseCommand

from apps.core.static_bundles import build_bundles


class Command(BaseCommand):
    help = "Concatenate component CSS into static/css/bundles/ (source files remain SSOT)."

    def handle(self, *args, **options):
        self.stdout.write("Building CSS bundles…")
        written = build_bundles(quiet=False)
        self.stdout.write(self.style.SUCCESS(f"Done: {len(written)} bundles."))
