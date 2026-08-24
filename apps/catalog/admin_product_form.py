"""Форма товару: характеристики — по одному select на атрибут."""
from __future__ import annotations

from django import forms
from unfold.widgets import UnfoldAdminSelectWidget

from apps.catalog.models import Attribute, AttributeValue, Product

ATTR_FIELD_PREFIX = "attr_select_"


def _attr_field_name(attribute_id: int) -> str:
    return f"{ATTR_FIELD_PREFIX}{attribute_id}"


class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        exclude = ("is_active", "slug", "attribute_values", "search_text", "popularity")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        selected: dict[int, int] = {}
        if self.instance and self.instance.pk:
            for av in self.instance.attribute_values.all().only("id", "attribute_id"):
                selected.setdefault(av.attribute_id, av.pk)

        attributes = (
            Attribute.objects.filter(is_filterable=True)
            .prefetch_related("values")
            .order_by("sort_order", "name_uk")
        )
        self._attribute_ids: list[int] = []
        for attr in attributes:
            field_name = _attr_field_name(attr.pk)
            self._attribute_ids.append(attr.pk)
            field = forms.ModelChoiceField(
                label=attr.name_uk,
                queryset=AttributeValue.objects.filter(attribute=attr).order_by(
                    "sort_order", "name_uk"
                ),
                required=False,
                empty_label="— не обрано —",
                initial=selected.get(attr.pk),
                widget=UnfoldAdminSelectWidget(),
            )
            field.label_from_instance = lambda obj: (obj.name_uk or str(obj.pk))
            self.fields[field_name] = field

    def save_attribute_values(self) -> None:
        if not self.instance.pk:
            return
        chosen: list[AttributeValue] = []
        for attr_id in self._attribute_ids:
            value = self.cleaned_data.get(_attr_field_name(attr_id))
            if value is not None:
                chosen.append(value)
        self.instance.attribute_values.set(chosen)


def attribute_select_field_names() -> tuple[str, ...]:
    return tuple(
        _attr_field_name(pk)
        for pk in Attribute.objects.filter(is_filterable=True)
        .order_by("sort_order", "name_uk")
        .values_list("pk", flat=True)
    )
