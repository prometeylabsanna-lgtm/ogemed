"""Seed секцій юридичних сторінок з hardcoded defaults (ідемпотентно)."""
from django.core.management.base import BaseCommand

from apps.cms.info_page_models import InfoPageMeta, InfoPageSection
from apps.cms.info_page_service import seed_meta_payloads, seed_payloads


class Command(BaseCommand):
    help = "Idempotent seed of InfoPageSection + InfoPageMeta."

    def handle(self, *args, **options):
        created = 0
        for payload in seed_payloads():
            _, was_created = InfoPageSection.objects.get_or_create(
                page_key=payload["page_key"],
                sort_order=payload["sort_order"],
                defaults={
                    "layout": payload["layout"],
                    "heading_uk": payload["heading_uk"],
                    "heading_ru": payload["heading_ru"],
                    "subheading_uk": payload["subheading_uk"],
                    "subheading_ru": payload["subheading_ru"],
                    "body_uk": payload["body_uk"],
                    "body_ru": payload["body_ru"],
                    "is_active": True,
                },
            )
            if was_created:
                created += 1

        meta_created = 0
        for payload in seed_meta_payloads():
            page_key = payload["page_key"]
            defaults = {k: v for k, v in payload.items() if k != "page_key"}
            _, was_created = InfoPageMeta.objects.get_or_create(
                page_key=page_key,
                defaults=defaults,
            )
            if was_created:
                meta_created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Info sections: +{created}, meta: +{meta_created}"
            )
        )
