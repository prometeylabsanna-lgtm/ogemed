"""Idempotent PDP demo: attributes, Pure Active variants matrix, characteristics."""
from __future__ import annotations

from decimal import Decimal

from apps.catalog.demo_product_copy import PRODUCT_COPY
from apps.catalog.models import (
    Attribute,
    AttributeValue,
    Availability,
    Product,
    ProductImage,
    ProductVariant,
)


def _attr(
    slug: str,
    name_uk: str,
    name_ru: str,
    sort_order: int,
    *,
    is_filterable: bool = True,
) -> Attribute:
    obj, _ = Attribute.objects.update_or_create(
        slug=slug,
        defaults={
            "name_uk": name_uk,
            "name_ru": name_ru,
            "is_filterable": is_filterable,
            "sort_order": sort_order,
        },
    )
    return obj


def _value(
    attribute: Attribute,
    slug: str,
    name_uk: str,
    name_ru: str,
    sort_order: int,
    color_hex: str = "",
) -> AttributeValue:
    obj, _ = AttributeValue.objects.update_or_create(
        attribute=attribute,
        slug=slug,
        defaults={
            "name_uk": name_uk,
            "name_ru": name_ru,
            "sort_order": sort_order,
            "color_hex": color_hex,
        },
    )
    return obj


def seed_catalog_attributes() -> dict[str, AttributeValue]:
    """Shared attribute dictionary for filters + PDP characteristics."""
    obyem = _attr("obyem", "Обʼєм", "Объём", 10)
    # Колір лишаємо в БД для старих даних, але не показуємо у фільтрах/PDP.
    _attr("kolir", "Колір", "Цвет", 20, is_filterable=False)
    rozmir = _attr("rozmir", "Розмір", "Размер", 30)
    kraina = _attr("kraina", "Країна виробник", "Страна производитель", 40)
    care = _attr("typ-doglyadu", "Тип догляду", "Тип ухода", 45)
    typ = _attr("typ-shkiry", "Тип шкіри", "Тип кожи", 50)
    ingredients = _attr(
        "aktyvni-ingredienty",
        "Активні інгредієнти",
        "Активные ингредиенты",
        60,
    )

    values = {
        "vol_1": _value(obyem, "1-ml", "1 мл", "1 мл", 1),
        "vol_3": _value(obyem, "3-ml", "3 мл", "3 мл", 2),
        "vol_5": _value(obyem, "5-ml", "5 мл", "5 мл", 3),
        "vol_9": _value(obyem, "9-ml", "9 мл", "9 мл", 4),
        "vol_10": _value(obyem, "10-ml", "10 мл", "10 мл", 5),
        "vol_30": _value(obyem, "30-ml", "30 мл", "30 мл", 6),
        "vol_50": _value(obyem, "50-ml", "50 мл", "50 мл", 7),
        "vol_75": _value(obyem, "75-ml", "75 мл", "75 мл", 8),
        "vol_100": _value(obyem, "100-ml", "100 мл", "100 мл", 9),
        "vol_200": _value(obyem, "200-ml", "200 мл", "200 мл", 10),
        "vol_225": _value(obyem, "225-ml", "225 мл", "225 мл", 11),
        "vol_250": _value(obyem, "250-ml", "250 мл", "250 мл", 12),
        "vol_500": _value(obyem, "500-ml", "500 мл", "500 мл", 13),
        "vol_887": _value(obyem, "887-ml", "887 мл", "887 мл", 14),
        "vol_1000": _value(obyem, "1000-ml", "1000 мл", "1000 мл", 15),
        "vol_2000": _value(obyem, "2000-ml", "2000 мл", "2000 мл", 16),
        "size_s": _value(rozmir, "s", "S", "S", 1),
        "size_m": _value(rozmir, "m", "M", "M", 2),
        "country_ua": _value(kraina, "ukrayina", "Україна", "Украина", 1),
        "country_kr": _value(kraina, "koreya", "Корея", "Корея", 2),
        "country_fr": _value(kraina, "frantsiya", "Франція", "Франция", 3),
        "care_home": _value(
            care,
            "dlya-domashnogo-doglyadu",
            "Для домашнього догляду",
            "Для домашнего ухода",
            1,
        ),
        "skin_sensitive": _value(typ, "chutlyva", "Чутлива", "Чувствительная", 1),
        "skin_dry": _value(typ, "sukha", "Суха", "Сухая", 2),
        "skin_normal": _value(typ, "normalna", "Нормальна", "Нормальная", 3),
        "skin_combo": _value(typ, "kombinovana", "Комбінована", "Комбинированная", 4),
        "skin_mature": _value(typ, "zrila", "Зріла", "Зрелая", 5),
        "skin_dull": _value(typ, "tumyana", "Тьмяна", "Тусклая", 6),
        "ing_niacinamide": _value(
            ingredients,
            "niacynamid",
            "Ніацинамід, пантенол",
            "Ниацинамид, пантенол",
            1,
        ),
        "ing_vit_c": _value(
            ingredients,
            "vitamin-c",
            "Вітамін C, ферулова кислота",
            "Витамин C, феруловая кислота",
            2,
        ),
        "ing_ceramides": _value(
            ingredients,
            "ceramidy",
            "Цераміди, сквалан",
            "Церамиды, сквалан",
            3,
        ),
        "ing_peptides": _value(
            ingredients,
            "peptydy",
            "Пептиди, колоїдне золото",
            "Пептиды, коллоидное золото",
            4,
        ),
        "ing_ha": _value(
            ingredients,
            "hialuron",
            "Гіалуронова кислота",
            "Гиалуроновая кислота",
            5,
        ),
        "ing_shea": _value(
            ingredients,
            "maslo-shy",
            "Олія ши, сквалан",
            "Масло ши, сквалан",
            6,
        ),
        "ing_jojoba": _value(
            ingredients,
            "zhozhoba",
            "Олія жожоба, сквалан",
            "Масло жожоба, сквалан",
            7,
        ),
        "ing_retinol": _value(
            ingredients,
            "retinol",
            "Ретинол 0,3%, бурштинова кислота",
            "Ретинол 0,3%, янтарная кислота",
            8,
        ),
        "ing_panthenol": _value(
            ingredients,
            "pantenol-troyanda",
            "Пантенол, гідролат троянди",
            "Пантенол, гидролат розы",
            9,
        ),
        "ing_collagen": _value(
            ingredients,
            "kolagen",
            "Гідролізований колаген, пептиди",
            "Гидролизованный коллаген, пептиды",
            10,
        ),
    }
    AttributeValue.objects.filter(attribute=obyem, slug="7x2-ml").delete()
    AttributeValue.objects.filter(attribute__slug="kolir").delete()
    return values


def seed_all_product_characteristics(
    values: dict[str, AttributeValue] | None = None,
) -> int:
    """Привʼязати характеристики (product.attribute_values) до всіх seed-товарів."""
    values = values or seed_catalog_attributes()
    updated = 0
    for slug, copy in PRODUCT_COPY.items():
        product = Product.objects.filter(slug=slug).first()
        if product is None:
            continue
        attr_list = []
        for key in copy.get("attrs", []):
            if key not in values:
                raise KeyError(f"Unknown attribute key '{key}' for product '{slug}'")
            attr_list.append(values[key])
        product.attribute_values.set(attr_list)
        updated += 1
    return updated


def _upsert_variant(
    product: Product,
    *,
    sku: str,
    label_uk: str,
    label_ru: str,
    price: str,
    old_price: str | None,
    stock: int,
    sort_order: int,
    attr_values: list[AttributeValue],
) -> ProductVariant:
    variant, _ = ProductVariant.objects.update_or_create(
        sku=sku,
        defaults={
            "product": product,
            "label_uk": label_uk,
            "label_ru": label_ru,
            "price": Decimal(price),
            "old_price": Decimal(old_price) if old_price else None,
            "stock": stock,
            "availability": "",
            "is_active": True,
            "sort_order": sort_order,
        },
    )
    variant.attribute_values.set(attr_values)
    return variant


def seed_pure_active_pdp(values: dict[str, AttributeValue] | None = None) -> None:
    """Варіанти лише за обʼємом для serum-pure-active (без кольору)."""
    values = values or seed_catalog_attributes()
    product = Product.objects.filter(slug="serum-pure-active").first()
    if product is None:
        return

    product.availability = Availability.IN_STOCK
    product.save(update_fields=["availability", "updated_at"])

    matrix = [
        {
            "sku": "OGM-SER-PA50",
            "label_uk": "50 мл",
            "label_ru": "50 мл",
            "price": "980.00",
            "old_price": None,
            "stock": 20,
            "sort_order": 0,
            "attrs": [values["vol_50"]],
        },
        {
            "sku": "OGM-SER-PA100",
            "label_uk": "100 мл",
            "label_ru": "100 мл",
            "price": "1450.00",
            "old_price": "1590.00",
            "stock": 8,
            "sort_order": 1,
            "attrs": [values["vol_100"]],
        },
    ]

    keep_skus = set()
    for row in matrix:
        _upsert_variant(
            product,
            sku=row["sku"],
            label_uk=row["label_uk"],
            label_ru=row["label_ru"],
            price=row["price"],
            old_price=row["old_price"],
            stock=row["stock"],
            sort_order=row["sort_order"],
            attr_values=row["attrs"],
        )
        keep_skus.add(row["sku"])

    product.variants.exclude(sku__in=keep_skus).update(is_active=False)

    images = list(product.images.order_by("-is_main", "sort_order", "id"))
    if images:
        ProductImage.objects.filter(pk=images[0].pk).update(variant=None)
    # Кольорові варіанти прибрані — відвʼязуємо їхні зображення.
    ProductImage.objects.filter(
        product=product,
        variant__sku__in=("OGM-SER-PA50-G", "OGM-SER-PA100-G"),
    ).update(variant=None)
