from django.core.management.base import BaseCommand

from apps.catalog.models import Brand

# Догляд (Косметика).
CARE_BRANDS = [
    ("biolab", "Biolab"),
    ("isov-sorex-skin-care", "Isov Sorex Skin Care"),
    ("toskani", "Toskani"),
    ("massena", "Massena"),
    ("promoitalia", "Promoitalia"),
    ("lamic", "Lamic"),
    ("tebiskin", "Tebiskin"),
    ("sesderma", "Sesderma"),
    ("cure-skin", "Cure Skin"),
    ("renew", "Renew"),
    ("pelart-laboratory", "Pelart Laboratory"),
    ("dr-kadir", "Dr.Kadir"),
    ("holy-land", "Holy Land"),
    ("histolab", "Histolab"),
    ("esthemax", "Esthemax"),
    ("pharmely", "Pharmely"),
    ("genosys", "Genosys"),
    ("endor", "Endor"),
    ("thermo-ceutical", "tHermoCeutical"),
    ("prx-t33", "PRX-T33"),
]

# Ін'єкційні. Спільні з доглядом: Toskani, Massena, Promoitalia.
INJECTABLE_BRANDS = [
    ("infini", "INFINI"),
    ("promoitalia", "Promoitalia"),
    ("toskani", "Toskani"),
    ("massena", "Massena"),
    ("eldermafill", "Eldermafill"),
    ("medixa", "Medixa"),
]

# Existing demo brands keep lower sort_order; new ones start below them.
START_ORDER = 100


class Command(BaseCommand):
    help = "Idempotent brand seed (name + slug). Never overwrites cover/showcase images."

    def handle(self, *args, **options):
        by_slug: dict[str, dict] = {}
        for index, (slug, name) in enumerate(CARE_BRANDS):
            entry = by_slug.setdefault(
                slug,
                {"name": name, "order": START_ORDER + index},
            )
            entry["name"] = name
        offset = len(CARE_BRANDS)
        for index, (slug, name) in enumerate(INJECTABLE_BRANDS):
            entry = by_slug.setdefault(
                slug,
                {"name": name, "order": START_ORDER + offset + index},
            )
            entry["name"] = name

        created = updated = 0
        for slug, data in by_slug.items():
            brand, was_created = Brand.objects.get_or_create(
                slug=slug,
                defaults={
                    "name_uk": data["name"],
                    "name_ru": data["name"],
                    "is_active": True,
                    "sort_order": data["order"],
                },
            )
            if was_created:
                created += 1
            else:
                brand.name_uk = data["name"]
                brand.name_ru = data["name"]
                brand.is_active = True
                brand.save(update_fields=["name_uk", "name_ru", "is_active", "updated_at"])
                updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Brands: {created} created, {updated} updated, "
                f"{len(by_slug)} total in seed list."
            )
        )
