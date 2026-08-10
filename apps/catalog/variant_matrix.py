"""PDP variant option matrix: Обʼєм / Колір / Розмір groups."""
from __future__ import annotations

from dataclasses import dataclass

from .models import Attribute, AttributeValue, ProductVariant

COLOR_ATTR_SLUGS = frozenset({"kolir", "color", "colour", "cvet", "цвет"})


@dataclass(frozen=True)
class VariantOption:
    value: AttributeValue
    target_variant: ProductVariant | None
    is_selected: bool
    is_available: bool

    @property
    def is_swatch(self) -> bool:
        return bool(self.value.color_hex)

    @property
    def swatch_color(self) -> str:
        return self.value.color_hex or ""


@dataclass(frozen=True)
class VariantOptionGroup:
    attribute: Attribute
    options: list[VariantOption]

    @property
    def is_color(self) -> bool:
        if self.attribute.slug in COLOR_ATTR_SLUGS:
            return True
        return any(opt.is_swatch for opt in self.options)


def _variant_value_map(variant: ProductVariant) -> dict[int, int]:
    return {av.attribute_id: av.pk for av in variant.attribute_values.all()}


def resolve_variant_for_option(
    variants: list[ProductVariant],
    active: ProductVariant | None,
    attribute_id: int,
    value_id: int,
) -> tuple[ProductVariant | None, bool]:
    """Pick the best variant when choosing one attribute value.

    Returns (variant, compatible_with_other_axes).
    """
    active_map = _variant_value_map(active) if active else {}
    desired = {**active_map, attribute_id: value_id}

    for variant in variants:
        vmap = _variant_value_map(variant)
        if all(vmap.get(aid) == vid for aid, vid in desired.items()):
            return variant, True

    for variant in variants:
        vmap = _variant_value_map(variant)
        if vmap.get(attribute_id) == value_id:
            return variant, False

    return None, False


def build_variant_option_groups(
    variants: list[ProductVariant],
    active: ProductVariant | None,
) -> list[VariantOptionGroup]:
    """Attribute-based option groups for PDP. Empty if <2 variants or no attrs."""
    if len(variants) < 2:
        return []

    attrs: dict[int, Attribute] = {}
    values_by_attr: dict[int, dict[int, AttributeValue]] = {}
    for variant in variants:
        for av in variant.attribute_values.all():
            attrs[av.attribute_id] = av.attribute
            values_by_attr.setdefault(av.attribute_id, {})[av.pk] = av

    if not attrs:
        return []

    active_map = _variant_value_map(active) if active else {}
    groups: list[VariantOptionGroup] = []

    for attr in sorted(attrs.values(), key=lambda a: (a.sort_order, a.pk)):
        options: list[VariantOption] = []
        for value in sorted(
            values_by_attr[attr.pk].values(),
            key=lambda v: (v.sort_order, v.pk),
        ):
            target, compatible = resolve_variant_for_option(
                variants, active, attr.pk, value.pk
            )
            options.append(
                VariantOption(
                    value=value,
                    target_variant=target,
                    is_selected=active_map.get(attr.pk) == value.pk,
                    is_available=target is not None and compatible,
                )
            )
        groups.append(VariantOptionGroup(attribute=attr, options=options))

    return groups


def uses_flat_variant_labels(
    variants: list[ProductVariant],
    groups: list[VariantOptionGroup],
) -> bool:
    """True when we should show label buttons instead of attribute matrix."""
    return len(variants) > 1 and not groups
