"""Ідемпотентний seed усіх SiteBlock з registry."""
from django.core.management.base import BaseCommand

from apps.core.admin_site_content import load_section_blocks
from apps.core.block_defaults import default_pair
from apps.core.models import SiteBlock, SiteSettings
from apps.core.site_content_registry import CONTENT_SECTIONS, iter_section_blocks


class Command(BaseCommand):
    help = "Seed SiteBlock rows from CONTENT_SECTIONS (no overwrite)."

    def handle(self, *args, **options):
        SiteSettings.objects.get_or_create(pk=1)
        created = 0
        for section in CONTENT_SECTIONS:
            before = SiteBlock.objects.count()
            load_section_blocks(section)
            created += SiteBlock.objects.count() - before
        # sanity: every registry key exists
        missing = []
        for section in CONTENT_SECTIONS:
            for page, key in iter_section_blocks(section):
                if not SiteBlock.objects.filter(page=page, key=key).exists():
                    uk, ru = default_pair(page, key)
                    missing.append((page, key, uk, ru))
        self.stdout.write(
            self.style.SUCCESS(
                f"SiteBlocks ready. New rows this run: {created}. Missing: {len(missing)}."
            )
        )
