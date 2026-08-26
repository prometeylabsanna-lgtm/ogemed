"""Фільтри товарів в адмінці за значеннями Attribute (тип шкіри, обʼєм тощо)."""
from __future__ import annotations

from collections.abc import Generator
from typing import Any

from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from unfold.contrib.filters.forms import DropdownForm

from apps.core.admin_filters import _filter_label
from apps.catalog.models import AttributeValue

# slug Attribute → підпис фільтра в адмінці
PRODUCT_ATTR_FILTERS: tuple[tuple[str, str], ...] = (
    ("typ-shkiry", "Тип шкіри"),
    ("zastosuvannya", "Застосування"),
    ("obyem", "Обʼєм"),
    ("kraina", "Країна виробник"),
)


def _make_attribute_filter(attribute_slug: str, title: str):
    param = f"attr_{attribute_slug.replace('-', '_')}"

    class _ProductAttributeFilter(admin.SimpleListFilter):
        template = "unfold/filters/filters_field.html"
        form_class = DropdownForm
        all_option = ["", "Всі"]

        def lookups(self, request, model_admin):
            return list(
                AttributeValue.objects.filter(attribute__slug=attribute_slug)
                .order_by("sort_order", "name_uk")
                .values_list("pk", "name_uk")
            )

        def queryset(self, request, queryset: QuerySet) -> QuerySet:
            value = self.value()
            if not value:
                return queryset
            return queryset.filter(
                attribute_values__attribute__slug=attribute_slug,
                attribute_values__pk=value,
            ).distinct()

        def has_output(self) -> bool:
            # завжди показуємо фільтр, навіть якщо значень ще немає
            return True

        def choices(self, changelist: ChangeList) -> Generator[dict[str, Any], None, None]:
            choices = [self.all_option, *(self.lookup_choices or [])]
            yield {
                "form": self.form_class(
                    label=_filter_label(self.title),
                    name=self.parameter_name,
                    choices=choices,
                    data={self.parameter_name: self.value() or ""},
                ),
            }

    _ProductAttributeFilter.title = _(title)
    _ProductAttributeFilter.parameter_name = param
    _ProductAttributeFilter.__name__ = f"AttrFilter_{param}"
    _ProductAttributeFilter.__qualname__ = _ProductAttributeFilter.__name__
    return _ProductAttributeFilter


PRODUCT_ATTRIBUTE_ADMIN_FILTERS: tuple[type[admin.SimpleListFilter], ...] = tuple(
    _make_attribute_filter(slug, title) for slug, title in PRODUCT_ATTR_FILTERS
)
