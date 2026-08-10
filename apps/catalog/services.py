"""Catalog query helpers."""
from __future__ import annotations

from decimal import Decimal, InvalidOperation

from django.db.models import Min, Prefetch, Q, QuerySet
from django.utils.translation import gettext_lazy as _

from .labels import label_by_slug
from .models import Attribute, Brand, Category, Product, ProductVariant

CATALOG_SORT_OPTIONS = (
    ("novelty", _("Новизна")),
    ("popularity", _("Популярність")),
    ("price_asc", _("Ціна: спочатку дешевші")),
    ("price_desc", _("Ціна: спочатку дорожчі")),
)

CATALOG_VIEW_OPTIONS = (
    ("grid", _("Сітка")),
    ("list", _("Список")),
)

CATALOG_VIEW_VALUES = {value for value, _label in CATALOG_VIEW_OPTIONS}

CATALOG_FILTER_KEYS = (
    "brand",
    "price_min",
    "price_max",
    "attr",
    "availability",
    "label",
    "skin_type",
)

SKIN_TYPE_ATTR_SLUG = "typ-shkiry"
SKIN_TYPE_SELECT = "select"


def resolve_catalog_view(params) -> str:
    view = (params.get("view") if params is not None else None) or "grid"
    return view if view in CATALOG_VIEW_VALUES else "grid"


def published_products() -> QuerySet[Product]:
    return (
        Product.objects.published()
        .select_related("brand", "primary_category")
        .prefetch_related("images", "variants")
        .with_price()
    )


def apply_catalog_filters(qs: QuerySet[Product], params) -> QuerySet[Product]:
    brand = params.get("brand")
    if brand:
        qs = qs.filter(brand__slug=brand)

    category = params.get("category")
    if category:
        qs = qs.filter(
            Q(primary_category__slug=category) | Q(categories__slug=category)
        ).distinct()

    try:
        price_min = Decimal(params.get("price_min") or "")
        qs = qs.filter(min_price__gte=price_min)
    except (InvalidOperation, TypeError):
        pass

    try:
        price_max = Decimal(params.get("price_max") or "")
        qs = qs.filter(min_price__lte=price_max)
    except (InvalidOperation, TypeError):
        pass

    attr_slugs = params.getlist("attr") if hasattr(params, "getlist") else []
    for slug in attr_slugs:
        if slug:
            qs = qs.filter(attribute_values__slug=slug)
    if attr_slugs:
        qs = qs.distinct()

    availability = params.get("availability")
    if availability:
        qs = qs.filter(availability=availability)

    label = label_by_slug(params.get("label"))
    if label is not None:
        qs = qs.filter(**{label.field: True})

    skin_type = (params.get("skin_type") or "").strip()
    if skin_type and skin_type != SKIN_TYPE_SELECT:
        qs = qs.filter(
            attribute_values__slug=skin_type,
            attribute_values__attribute__slug=SKIN_TYPE_ATTR_SLUG,
        ).distinct()

    return qs


def apply_catalog_sort(qs: QuerySet[Product], sort: str | None) -> QuerySet[Product]:
    mapping = {
        "price_asc": ("min_price", "id"),
        "price_desc": ("-min_price", "id"),
        "popularity": ("-popularity", "-created_at"),
        "novelty": ("-created_at",),
        "name": ("name_uk",),
    }
    order = mapping.get(sort or "novelty", ("-created_at",))
    return qs.order_by(*order)


def search_products(query: str) -> QuerySet[Product]:
    q = (query or "").strip().casefold()
    qs = published_products()
    if not q:
        return qs.none()
    return (
        qs.filter(
            Q(search_text__icontains=q)
            | Q(name_uk__icontains=query)
            | Q(name_ru__icontains=query)
            | Q(variants__sku__icontains=query)
        )
        .distinct()
        .order_by("-popularity", "-created_at")
    )


def hits_products(limit: int = 8) -> QuerySet[Product]:
    return published_products().filter(is_hit=True)[:limit]


def new_products(limit: int = 8) -> QuerySet[Product]:
    return published_products().filter(is_new=True).order_by("-created_at")[:limit]


def top_level_categories():
    return Category.objects.filter(is_active=True, parent=None).order_by(
        "sort_order", "name_uk"
    )


def home_quick_categories(limit: int = 8):
    """Категорії з прапорцем show_on_home для блоку на головній."""
    return (
        Category.objects.filter(is_active=True, show_on_home=True)
        .order_by("sort_order", "name_uk")[:limit]
    )


def category_branch_ids(category: Category) -> list[int]:
    """Category plus its active descendants, so parent pages are not empty."""
    ids = [category.pk]
    frontier = [category.pk]
    while frontier:
        children = list(
            Category.objects.filter(is_active=True, parent_id__in=frontier).values_list(
                "pk", flat=True
            )
        )
        children = [pk for pk in children if pk not in ids]
        if not children:
            break
        ids.extend(children)
        frontier = children
    return ids


def nav_categories():
    """Top-level categories with active children for header dropdown."""
    children_qs = Category.objects.filter(is_active=True).order_by(
        "sort_order", "name_uk"
    )
    return top_level_categories().prefetch_related(
        Prefetch("children", queryset=children_qs)
    )


def catalog_controls_context() -> dict:
    """Brands, categories and attributes powering the catalog control bar."""
    return {
        "filter_brands": Brand.objects.filter(is_active=True),
        "filter_categories": nav_categories(),
        "filter_attributes": Attribute.objects.filter(is_filterable=True).prefetch_related(
            "values"
        ),
        "sort_options": CATALOG_SORT_OPTIONS,
        "view_options": CATALOG_VIEW_OPTIONS,
    }


def catalog_query_string(params, exclude=("page", "more")) -> str:
    """Current querystring without paging, used to keep filters across pages."""
    qd = params.copy()
    for key in exclude:
        if key in qd:
            del qd[key]
    for key in list(qd.keys()):
        values = [value for value in qd.getlist(key) if value]
        if values:
            qd.setlist(key, values)
        else:
            del qd[key]
    return qd.urlencode()


def has_active_filters(params) -> bool:
    for key in CATALOG_FILTER_KEYS:
        value = params.get(key)
        if not value:
            continue
        if key == "skin_type" and value == SKIN_TYPE_SELECT:
            continue
        return True
    return False


def is_skin_type_select(params) -> bool:
    return (params.get("skin_type") or "").strip() == SKIN_TYPE_SELECT


def get_active_variant(product: Product, variant_id: str | None) -> ProductVariant | None:
    variants = list(product.variants.filter(is_active=True))
    if not variants:
        return None
    if variant_id:
        for v in variants:
            if str(v.pk) == str(variant_id):
                return v
    return variants[0]


def variant_gallery(product: Product, variant: ProductVariant | None):
    """Images for the active variant, or shared product images (variant=None)."""
    images = list(product.images.all())
    if not images:
        return []
    if variant is not None:
        variant_imgs = [img for img in images if img.variant_id == variant.pk]
        if variant_imgs:
            return variant_imgs
    shared = [img for img in images if img.variant_id is None]
    return shared or images
