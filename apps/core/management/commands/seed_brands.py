from django.core.management.base import BaseCommand

from apps.catalog.models import Brand, Category

# Догляд (Косметика). Дублікати з ін'єкційними — один бренд, обидві категорії.
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

CAT_COSMETICS = "kosmetyka"
CAT_INJECTIONS = "inektsijni-preparaty"

# Existing demo brands keep lower sort_order; new ones start below them.
START_ORDER = 100


class Command(BaseCommand):
    help = (
        "Idempotent brand seed (name + slug + category links). "
        "Never overwrites logos uploaded through the admin."
    )

    def handle(self, *args, **options):
        cosmetics = Category.objects.filter(slug=CAT_COSMETICS, is_active=True).first()
        injections = Category.objects.filter(slug=CAT_INJECTIONS, is_active=True).first()
        if cosmetics is None or injections is None:
            self.stderr.write(
                self.style.ERROR(
                    "Categories kosmetyka / inektsijni-preparaty missing. "
                    "Run seed_catalog first."
                )
            )
            return

        by_slug: dict[str, dict] = {}
        for index, (slug, name) in enumerate(CARE_BRANDS):
            entry = by_slug.setdefault(
                slug,
                {"name": name, "cats": set(), "order": START_ORDER + index},
            )
            entry["name"] = name
            entry["cats"].add(cosmetics)
        offset = len(CARE_BRANDS)
        for index, (slug, name) in enumerate(INJECTABLE_BRANDS):
            entry = by_slug.setdefault(
                slug,
                {"name": name, "cats": set(), "order": START_ORDER + offset + index},
            )
            entry["name"] = name
            entry["cats"].add(injections)

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
            brand.categories.set(data["cats"])

        self.stdout.write(
            self.style.SUCCESS(
                f"Brands: {created} created, {updated} updated, "
                f"{len(by_slug)} total in seed list."
            )
        )
