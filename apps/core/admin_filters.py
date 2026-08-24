"""
Dropdown-фільтри Unfold з короткими українськими підписами (без «За …»).
"""
from __future__ import annotations

from collections.abc import Generator
from typing import Any

from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
from unfold.contrib.filters.admin import ChoicesDropdownFilter, RelatedDropdownFilter
from unfold.contrib.filters.admin.mixins import ValueMixin
from unfold.contrib.filters.forms import DropdownForm


def _filter_label(title: Any) -> str:
    label = str(title or "").strip()
    if not label:
        return ""
    return label[0].upper() + label[1:]


class UkChoicesDropdownFilter(ChoicesDropdownFilter):
    """ChoicesDropdownFilter з чистим підписом поля."""

    all_option = ["", "Всі"]

    def choices(self, changelist: ChangeList) -> Generator[dict[str, Any], None, None]:
        choices = [self.all_option, *self.field.flatchoices]
        yield {
            "form": self.form_class(
                label=_filter_label(self.title),
                name=self.lookup_kwarg,
                choices=choices,
                data={self.lookup_kwarg: self.value() or ""},
                multiple=self.multiple if hasattr(self, "multiple") else False,
            ),
        }


class UkRelatedDropdownFilter(RelatedDropdownFilter):
    """RelatedDropdownFilter з чистим підписом поля."""

    all_option = ["", "Всі"]

    def choices(self, changelist: ChangeList) -> Generator[dict[str, Any], None, None]:
        add_facets = changelist.add_facets
        facet_counts = self.get_facet_queryset(changelist) if add_facets else None

        if add_facets:
            choices = [self.all_option]
            for pk_val, val in self.lookup_choices:
                count = facet_counts[f"{pk_val}__c"]
                choices.append((pk_val, f"{val} ({count})"))
        else:
            choices = [self.all_option, *self.lookup_choices]

        yield {
            "form": self.form_class(
                label=_filter_label(self.title),
                name=self.lookup_kwarg,
                choices=choices,
                data={self.lookup_kwarg: self.value() or ""},
                multiple=self.multiple if hasattr(self, "multiple") else False,
            ),
        }


class UkBooleanDropdownFilter(ValueMixin, admin.BooleanFieldListFilter):
    """BooleanField як <select>: Всі / Так / Ні."""

    template = "unfold/filters/filters_field.html"
    form_class = DropdownForm
    all_option = ["", "Всі"]

    def choices(self, changelist: ChangeList) -> Generator[dict[str, Any], None, None]:
        choices = [
            self.all_option,
            ["1", "Так"],
            ["0", "Ні"],
        ]
        yield {
            "form": self.form_class(
                label=_filter_label(self.title),
                name=self.lookup_kwarg,
                choices=choices,
                data={self.lookup_kwarg: self.value() or ""},
            ),
        }


class UkAllValuesDropdownFilter(ValueMixin, admin.AllValuesFieldListFilter):
    """AllValuesField як <select> з чистим підписом."""

    template = "unfold/filters/filters_field.html"
    form_class = DropdownForm
    all_option = ["", "Всі"]

    def choices(self, changelist: ChangeList) -> Generator[dict[str, Any], None, None]:
        values = []
        for val in self.lookup_choices:
            if val is None or val == "":
                continue
            values.append((val, str(val)))
        choices = [self.all_option, *values]
        yield {
            "form": self.form_class(
                label=_filter_label(self.title),
                name=self.lookup_kwarg,
                choices=choices,
                data={self.lookup_kwarg: self.value() or ""},
            ),
        }


class UkActionFlagDropdownFilter(UkChoicesDropdownFilter):
    """Тип дії LogEntry — dropdown з узгодженими UK-підписами."""

    def __init__(self, field, request, params, model, model_admin, field_path):
        super().__init__(field, request, params, model, model_admin, field_path)
        self.title = "Тип дії"

    def choices(self, changelist: ChangeList) -> Generator[dict[str, Any], None, None]:
        from django.contrib.admin.models import ADDITION, CHANGE, DELETION

        choices = [
            self.all_option,
            [str(ADDITION), "Додавання"],
            [str(CHANGE), "Зміна"],
            [str(DELETION), "Видалення"],
        ]
        yield {
            "form": self.form_class(
                label=_filter_label(self.title),
                name=self.lookup_kwarg,
                choices=choices,
                data={self.lookup_kwarg: self.value() or ""},
                multiple=self.multiple if hasattr(self, "multiple") else False,
            ),
        }


class DropdownFiltersMixin:
    """Фільтри зверху над таблицею, без бічної панелі."""

    list_filter_sheet = False
    list_filter_submit = True
