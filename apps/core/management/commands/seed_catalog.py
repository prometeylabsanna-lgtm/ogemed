import random
from decimal import Decimal
from pathlib import Path

from django.core.files import File
from django.core.management.base import BaseCommand

from apps.catalog.demo_pdp_data import (
    seed_all_product_characteristics,
    seed_catalog_attributes,
    seed_pure_active_pdp,
)
from apps.catalog.demo_product_copy import PRODUCT_COPY
from apps.catalog.labels import LABEL_FIELDS
from apps.catalog.models import (
    Availability,
    Brand,
    Category,
    Product,
    ProductImage,
    ProductVariant,
)
from apps.cms.models import HeroSlide

SEED_DIR = Path(__file__).resolve().parents[4] / "media" / "seed"

# Fallback, якщо для слага немає запису в PRODUCT_COPY
SHORT_DESC_UK = "Делікатна формула для щоденного догляду: легка текстура, швидко вбирається, не залишає липкості."
SHORT_DESC_RU = "Деликатная формула для ежедневного ухода: лёгкая текстура, быстро впитывается, без липкости."
DESC_UK = (
    "Засіб демо-вітрини OGEMED — базовий догляд для щоденного використання.\n\n"
    "Підходить для чутливої шкіри, легко поєднується з іншими продуктами лінії "
    "та не перевантажує шкіру."
)
DESC_RU = (
    "Средство демо-витрины OGEMED — базовый уход для ежедневного использования.\n\n"
    "Подходит для чувствительной кожи, легко сочетается с другими продуктами линии "
    "и не перегружает кожу."
)


def copy_for(slug: str) -> dict[str, str]:
    row = PRODUCT_COPY.get(slug) or {}
    return {
        "short_description_uk": row.get("short_uk") or SHORT_DESC_UK,
        "short_description_ru": row.get("short_ru") or SHORT_DESC_RU,
        "description_uk": row.get("desc_uk") or DESC_UK,
        "description_ru": row.get("desc_ru") or DESC_RU,
    }


def labels_for(slug: str) -> dict[str, bool]:
    """3–4 випадкові мітки з реєстру. Генератор сіється слагом, тому повторний
    запуск команди дає той самий набір — сід лишається ідемпотентним."""
    rng = random.Random(slug)
    chosen = set(rng.sample(LABEL_FIELDS, rng.choice((3, 4))))
    return {field: field in chosen for field in LABEL_FIELDS}


def brand_for(slug: str, brands: list[Brand]) -> Brand:
    """Демо-товари розкидані по наявних брендах: вибір теж сіється слагом,
    щоб фільтр за брендом давав стабільну вибірку між запусками."""
    return random.Random(f"{slug}:brand").choice(brands)


class Command(BaseCommand):
    help = "Idempotent catalog + hero seed (images overwrite)."

    def _attach_image(self, field, path: Path) -> None:
        if not path.is_file():
            self.stdout.write(self.style.WARNING(f"Missing image: {path}"))
            return
        if field.name:
            field.delete(save=False)
        with path.open("rb") as fh:
            field.save(path.name, File(fh), save=False)

    def handle(self, *args, **options):
        hero_defs = [
            {
                "sort_order": 1,
                "title_uk": "Догляд, який відчувається на шкірі",
                "title_ru": "Уход, который чувствуется на коже",
                "subtitle_uk": "Косметологічні формули для дому — концентрати активних компонентів у чистому вигляді.",
                "subtitle_ru": "Косметологические формулы для дома — концентраты активных компонентов в чистом виде.",
                "cta_label_uk": "До каталогу",
                "cta_label_ru": "В каталог",
                "cta_url": "/katalog/",
                "image": "hero-1.jpg",
            },
            {
                "sort_order": 2,
                "title_uk": "Сезон оновлення шкіри",
                "title_ru": "Сезон обновления кожи",
                "subtitle_uk": "Кислотні пілінги та сироватки для делікатного відновлення без роздратування.",
                "subtitle_ru": "Кислотные пилинги и сыворотки для деликатного восстановления без раздражения.",
                "cta_label_uk": "Дивитись хіти",
                "cta_label_ru": "Смотреть хиты",
                "cta_url": "/katalog/?sort=hit",
                "image": "hero-2.jpg",
            },
            {
                "sort_order": 3,
                "title_uk": "OGEMED for you: краса, якій довіряють",
                "title_ru": "OGEMED for you: красота, которой доверяют",
                "subtitle_uk": "Косметика, розроблена косметологами для салонного результату вдома.",
                "subtitle_ru": "Косметика, разработанная косметологами для салонного результата дома.",
                "cta_label_uk": "Про бренд",
                "cta_label_ru": "О бренде",
                "cta_url": "/pro-nas/",
                "image": "hero-3.jpg",
            },
        ]

        for item in hero_defs:
            slide, created = HeroSlide.objects.get_or_create(
                sort_order=item["sort_order"],
                defaults={
                    "title_uk": item["title_uk"],
                    "title_ru": item["title_ru"],
                    "subtitle_uk": item["subtitle_uk"],
                    "subtitle_ru": item["subtitle_ru"],
                    "cta_label_uk": item["cta_label_uk"],
                    "cta_label_ru": item["cta_label_ru"],
                    "cta_url": item["cta_url"],
                    "is_active": True,
                },
            )
            if not created:
                for key in (
                    "title_uk",
                    "title_ru",
                    "subtitle_uk",
                    "subtitle_ru",
                    "cta_label_uk",
                    "cta_label_ru",
                    "cta_url",
                ):
                    setattr(slide, key, item[key])
                slide.is_active = True
            self._attach_image(slide.image, SEED_DIR / item["image"])
            slide.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f"{'Created' if created else 'Updated'} HeroSlide #{slide.sort_order}"
                )
            )

        # Deactivate leftover slides that are not in seed set
        HeroSlide.objects.exclude(sort_order__in=[1, 2, 3]).update(is_active=False)

        # Top-level categories
        cosmetics_cat, _created = Category.objects.get_or_create(
            slug="kosmetyka",
            defaults={"name_uk": "Косметика", "name_ru": "Косметика", "is_active": True, "sort_order": 1},
        )
        injections_cat, _created = Category.objects.get_or_create(
            slug="inektsijni-preparaty",
            defaults={
                "name_uk": "Ін'єкційні препарати",
                "name_ru": "Инъекционные препараты",
                "is_active": True,
                "sort_order": 2,
            },
        )
        for cat, name_uk, name_ru, sort_order in (
            (cosmetics_cat, "Косметика", "Косметика", 1),
            (injections_cat, "Ін'єкційні препарати", "Инъекционные препараты", 2),
        ):
            cat.name_uk = name_uk
            cat.name_ru = name_ru
            cat.parent = None
            cat.is_active = True
            cat.sort_order = sort_order
            cat.save(update_fields=["name_uk", "name_ru", "parent", "is_active", "sort_order"])

        # Deactivate legacy subcategories (Обличчя / Тіло / Макіяж)
        Category.objects.filter(slug__in=("oblychchya", "tilo", "makiyazh")).update(
            is_active=False
        )

        subcategory_defs = [
            # Косметика
            {
                "slug": "uhodova-kosmetyka",
                "parent": cosmetics_cat,
                "sort_order": 1,
                "name_uk": "Доглядова косметика",
                "name_ru": "Уходовая косметика",
            },
            {
                "slug": "pilinhy",
                "parent": cosmetics_cat,
                "sort_order": 2,
                "name_uk": "Пілінги",
                "name_ru": "Пилинги",
            },
            {
                "slug": "masky",
                "parent": cosmetics_cat,
                "sort_order": 3,
                "name_uk": "Маски",
                "name_ru": "Маски",
            },
            {
                "slug": "ochyshchennya",
                "parent": cosmetics_cat,
                "sort_order": 4,
                "name_uk": "Очищення",
                "name_ru": "Очищение",
            },
            {
                "slug": "tonizatsiya",
                "parent": cosmetics_cat,
                "sort_order": 5,
                "name_uk": "Тонізація",
                "name_ru": "Тонизация",
            },
            # Ін'єкційні препарати
            {
                "slug": "filery",
                "parent": injections_cat,
                "sort_order": 1,
                "name_uk": "Філери",
                "name_ru": "Филлеры",
            },
            {
                "slug": "biorevitalizanty",
                "parent": injections_cat,
                "sort_order": 2,
                "name_uk": "Біоревіталізанти",
                "name_ru": "Биоревитализанты",
            },
            {
                "slug": "mezokoktejli",
                "parent": injections_cat,
                "sort_order": 3,
                "name_uk": "Мезококтейлі",
                "name_ru": "Мезококтейли",
            },
            {
                "slug": "kolagenostymulyatory",
                "parent": injections_cat,
                "sort_order": 4,
                "name_uk": "Колагеностимулятори",
                "name_ru": "Коллагеностимуляторы",
            },
            {
                "slug": "lipolityky",
                "parent": injections_cat,
                "sort_order": 5,
                "name_uk": "Ліполітики",
                "name_ru": "Липолитики",
            },
        ]
        cats_by_slug: dict[str, Category] = {}
        for item in subcategory_defs:
            cat, _created = Category.objects.get_or_create(
                slug=item["slug"],
                defaults={
                    "name_uk": item["name_uk"],
                    "name_ru": item["name_ru"],
                    "parent": item["parent"],
                    "is_active": True,
                    "sort_order": item["sort_order"],
                },
            )
            cat.name_uk = item["name_uk"]
            cat.name_ru = item["name_ru"]
            cat.parent = item["parent"]
            cat.is_active = True
            cat.sort_order = item["sort_order"]
            cat.save(
                update_fields=["name_uk", "name_ru", "parent", "is_active", "sort_order"]
            )
            cats_by_slug[item["slug"]] = cat
            self.stdout.write(self.style.SUCCESS(f"Category ready: {item['slug']}"))

        care = cats_by_slug["uhodova-kosmetyka"]
        toning = cats_by_slug["tonizatsiya"]
        masks = cats_by_slug["masky"]
        cleansing = cats_by_slug["ochyshchennya"]
        peels = cats_by_slug["pilinhy"]
        # keep aliases for product seed mapping
        face = care
        body = care
        makeup = care

        # Brands featured on the homepage showcase block
        brand_defs = [
            {
                "slug": "pharmely",
                "sort_order": 1,
                "name_uk": "Pharmely",
                "name_ru": "Pharmely",
                "tagline_uk": "Фармацевтична якість і клінічно доведена ефективність — формули, яким довіряють професіонали.",
                "tagline_ru": "Фармацевтическое качество и клинически доказанная эффективность — формулы, которым доверяют профессионалы.",
                "image": "brand-pharmely.png",
            },
            {
                "slug": "infini-premium",
                "sort_order": 2,
                "name_uk": "Infini Premium",
                "name_ru": "Infini Premium",
                "tagline_uk": "Преміальний догляд із делікатними текстурами для салонних і домашніх ритуалів краси.",
                "tagline_ru": "Премиальный уход с деликатными текстурами для салонных и домашних ритуалов красоты.",
                "image": "brand-infini-premium.png",
            },
            {
                "slug": "esthemax",
                "sort_order": 3,
                "name_uk": "Esthemax",
                "name_ru": "Esthemax",
                "tagline_uk": "Естетична косметологія нового рівня — інноваційні рішення для видимого результату.",
                "tagline_ru": "Эстетическая косметология нового уровня — инновационные решения для видимого результата.",
                "image": "brand-esthemax.png",
            },
        ]
        for item in brand_defs:
            featured_brand, created = Brand.objects.get_or_create(
                slug=item["slug"],
                defaults={
                    "name_uk": item["name_uk"],
                    "name_ru": item["name_ru"],
                    "tagline_uk": item["tagline_uk"],
                    "tagline_ru": item["tagline_ru"],
                    "is_featured": True,
                    "is_active": True,
                    "sort_order": item["sort_order"],
                },
            )
            if not created:
                featured_brand.name_uk = item["name_uk"]
                featured_brand.name_ru = item["name_ru"]
                featured_brand.tagline_uk = item["tagline_uk"]
                featured_brand.tagline_ru = item["tagline_ru"]
                featured_brand.is_featured = True
                featured_brand.is_active = True
                featured_brand.sort_order = item["sort_order"]
            # Вітрина на головній — окреме поле; cover_image для каталогу/brendy
            # лишається з import_brand_covers (media/brands/sources).
            # Джерела packshot: assets/gen2-{cream-bamboo,serum,spray}.png → media/seed/brand-*.png
            self._attach_image(featured_brand.showcase_image, SEED_DIR / item["image"])
            featured_brand.save()
            self.stdout.write(self.style.SUCCESS(f"Brand ready: {item['slug']}"))

        samples = [
            # Каталог / хіти (не в блоці Новинки)
            {
                "slug": "serum-vitamin-c",
                "name_uk": "Сироватка Vitamin C",
                "name_ru": "Сыворотка Vitamin C",
                "category": face,
                "is_hit": True,
                "is_new": False,
                "is_sale": True,
                "sku": "OGM-SER-C30",
                "price": "890.00",
                "old_price": "1090.00",
                "label_uk": "30 мл",
                "image": "serum-vitamin-c.jpg",
            },
            {
                "slug": "body-lotion-pure",
                "name_uk": "Лосьйон для тіла Pure",
                "name_ru": "Лосьон для тела Pure",
                "category": body,
                "is_hit": True,
                "is_new": False,
                "is_sale": False,
                "sku": "OGM-LOT-PR200",
                "price": "680.00",
                "old_price": None,
                "label_uk": "200 мл",
                "image": "body-lotion-pure.jpg",
            },
            {
                "slug": "serum-pump-gold",
                "name_uk": "Сироватка Gold Pump",
                "name_ru": "Сыворотка Gold Pump",
                "category": care,
                "is_hit": True,
                "is_new": False,
                "is_sale": False,
                "sku": "OGM-SER-GP50",
                "price": "1120.00",
                "old_price": None,
                "label_uk": "50 мл",
                "image": "serum-pump-gold.jpg",
            },
            {
                "slug": "cream-cheek-glow",
                "name_uk": "Крем Cheek Glow",
                "name_ru": "Крем Cheek Glow",
                "category": care,
                "is_hit": True,
                "is_new": False,
                "is_sale": False,
                "sku": "OGM-CRM-CG50",
                "price": "850.00",
                "old_price": None,
                "label_uk": "50 мл",
                "image": "cream-cheek-glow.jpg",
            },
            {
                "slug": "balm-silk",
                "name_uk": "Бальзам Silk Touch",
                "name_ru": "Бальзам Silk Touch",
                "category": care,
                "is_hit": True,
                "is_new": False,
                "is_sale": True,
                "sku": "OGM-BL-ST75",
                "price": "590.00",
                "old_price": "720.00",
                "label_uk": "75 мл",
                "image": "balm-silk.jpg",
            },
            # Новинки (7) — прозорі PNG packshots
            {
                "slug": "cream-soft-bamboo",
                "name_uk": "Крем Soft Bamboo",
                "name_ru": "Крем Soft Bamboo",
                "category": face,
                "is_hit": True,
                "is_new": True,
                "is_sale": False,
                "sku": "OGM-CRM-SB50",
                "price": "890.00",
                "old_price": None,
                "label_uk": "50 мл",
                "image": "novinka-v5-cream-bamboo.png",
            },
            {
                "slug": "oil-glow-mist",
                "name_uk": "Олія Glow Mist",
                "name_ru": "Масло Glow Mist",
                "category": care,
                "is_hit": False,
                "is_new": True,
                "is_sale": True,
                "sku": "OGM-OIL-GM100",
                "price": "720.00",
                "old_price": "890.00",
                "label_uk": "100 мл",
                "image": "novinka-v5-oil-glow-mist.png",
            },
            {
                "slug": "serum-amber-drop",
                "name_uk": "Сироватка Amber Drop",
                "name_ru": "Сыворотка Amber Drop",
                "category": care,
                "is_hit": True,
                "is_new": True,
                "is_sale": False,
                "sku": "OGM-SER-AD30",
                "price": "1180.00",
                "old_price": None,
                "label_uk": "30 мл",
                "image": "novinka-v5-serum-amber-drop.png",
            },
            {
                "slug": "cream-rose-soft-care",
                "name_uk": "Крем Rose Soft Care",
                "name_ru": "Крем Rose Soft Care",
                "category": face,
                "is_hit": False,
                "is_new": True,
                "is_sale": False,
                "sku": "OGM-CRM-RSC50",
                "price": "810.00",
                "old_price": None,
                "label_uk": "50 мл",
                "image": "novinka-v5-cream-rose-soft.png",
            },
            {
                "slug": "ampoules-collagen-boost",
                "name_uk": "Ампули Collagen Boost",
                "name_ru": "Ампулы Collagen Boost",
                "category": peels,
                "is_hit": True,
                "is_new": True,
                "is_sale": True,
                "sku": "OGM-AMP-CB7",
                "price": "1450.00",
                "old_price": "1690.00",
                "label_uk": "10 мл",
                "image": "novinka-v5-ampoules-collagen.png",
            },
            {
                "slug": "serum-pure-active",
                "name_uk": "Сироватка Pure Active",
                "name_ru": "Сыворотка Pure Active",
                "category": care,
                "is_hit": False,
                "is_new": True,
                "is_sale": False,
                "sku": "OGM-SER-PA50",
                "price": "980.00",
                "old_price": None,
                "label_uk": "50 мл",
                "image": "novinka-v5-serum-pure-active.png",
            },
            {
                "slug": "balm-repair-pot",
                "name_uk": "Бальзам Repair Pot",
                "name_ru": "Бальзам Repair Pot",
                "category": masks,
                "is_hit": True,
                "is_new": True,
                "is_sale": True,
                "sku": "OGM-BL-RP30",
                "price": "640.00",
                "old_price": "780.00",
                "label_uk": "30 мл",
                "image": "novinka-v5-balm-repair-pot.png",
            },
        ]

        seeded_slugs = {item["slug"] for item in samples}
        Product.objects.exclude(slug__in=seeded_slugs).filter(is_active=True).update(
            is_active=False
        )

        # order_by робить порядок незалежним від того, коли бренд додали в базу
        product_brands = list(Brand.objects.filter(is_active=True).order_by("slug"))

        for item in samples:
            labels = labels_for(item["slug"])
            texts = copy_for(item["slug"])
            item_brand = brand_for(item["slug"], product_brands)
            product, created = Product.objects.get_or_create(
                slug=item["slug"],
                defaults={
                    "name_uk": item["name_uk"],
                    "name_ru": item["name_ru"],
                    "brand": item_brand,
                    "primary_category": item["category"],
                    "availability": Availability.IN_STOCK,
                    "is_active": True,
                    "is_hit": item["is_hit"],
                    "is_new": item["is_new"],
                    "is_sale": item["is_sale"],
                    "sku": item["sku"],
                    "price": Decimal(item["price"]),
                    "old_price": Decimal(item["old_price"]) if item["old_price"] else None,
                    "stock": 20,
                    **texts,
                    **labels,
                },
            )
            if created:
                product.categories.add(item["category"])
                self.stdout.write(self.style.SUCCESS(f"Created product {item['slug']}"))
            else:
                product.name_uk = item["name_uk"]
                product.name_ru = item["name_ru"]
                product.is_hit = item["is_hit"]
                product.is_new = item["is_new"]
                product.is_sale = item["is_sale"]
                product.is_active = True
                product.brand = item_brand
                product.primary_category = item["category"]
                product.sku = item["sku"]
                product.price = Decimal(item["price"])
                product.old_price = (
                    Decimal(item["old_price"]) if item["old_price"] else None
                )
                product.stock = 20
                product.short_description_uk = texts["short_description_uk"]
                product.short_description_ru = texts["short_description_ru"]
                product.description_uk = texts["description_uk"]
                product.description_ru = texts["description_ru"]
                for field, value in labels.items():
                    setattr(product, field, value)
                product.save()
                self.stdout.write(f"Updated product {item['slug']}")

            product.categories.set([item["category"]])

            img_path = SEED_DIR / item["image"]
            main = product.images.filter(is_main=True).first() or product.images.first()
            if main is None:
                main = ProductImage(product=product, is_main=True, sort_order=0)
            else:
                main.is_main = True
                main.sort_order = 0
            self._attach_image(main.image, img_path)
            main.alt_uk = item["name_uk"]
            main.alt_ru = item["name_ru"]
            main.save()
            product.images.exclude(pk=main.pk).update(is_main=False)
            self.stdout.write(self.style.SUCCESS(f"Image set for {item['slug']}"))

            # Hover: завжди інший товарний файл (для помітної анімації).
            # Новинки (PNG packshot) → лише інший PNG без фону.
            # Хіти / lifestyle (JPG) → JPG з фоном.
            main_is_packshot = img_path.suffix.lower() == ".png"
            if main_is_packshot:
                hover_pool = [
                    "novinka-v5-serum-amber-drop.png",
                    "novinka-v5-cream-bamboo.png",
                    "novinka-v5-oil-glow-mist.png",
                    "novinka-v5-cream-rose-soft.png",
                    "novinka-v5-serum-pure-active.png",
                    "novinka-v5-balm-repair-pot.png",
                    "novinka-v5-ampoules-collagen.png",
                ]
            else:
                hover_pool = [
                    "serum-vitamin-c.jpg",
                    "body-lotion-pure.jpg",
                    "serum-pump-gold.jpg",
                    "cream-cheek-glow.jpg",
                    "balm-silk.jpg",
                    "cream-hydra.jpg",
                    "cream-velvet.jpg",
                    "toner-fresh.jpg",
                    "cream-spa-band.jpg",
                    "makeup-studio-kit.jpg",
                    "cream-rose-jar.jpg",
                    "foundation-glow.jpg",
                ]
            hover_pool = [
                f for f in hover_pool if f != item["image"] and (SEED_DIR / f).is_file()
            ]
            if hover_pool:
                hover_name = random.Random(f"{item['slug']}:hover-file").choice(hover_pool)
                hover = (
                    product.images.exclude(pk=main.pk).order_by("sort_order", "id").first()
                )
                if hover is None:
                    hover = ProductImage(product=product, is_main=False, sort_order=1)
                else:
                    hover.is_main = False
                    hover.sort_order = 1
                self._attach_image(hover.image, SEED_DIR / hover_name)
                hover.alt_uk = item["name_uk"]
                hover.alt_ru = item["name_ru"]
                hover.save()
                product.images.exclude(pk__in=[main.pk, hover.pk]).delete()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Hover image set for {item['slug']} ← {hover_name}"
                    )
                )
            else:
                product.images.exclude(pk=main.pk).delete()

        attr_values = seed_catalog_attributes()
        seeded_attrs = seed_all_product_characteristics(attr_values)
        seed_pure_active_pdp(attr_values)
        self.stdout.write(
            self.style.SUCCESS(
                f"PDP: characteristics for {seeded_attrs} products + Pure Active variants"
            )
        )
        self.stdout.write(self.style.SUCCESS("Catalog seed done"))
