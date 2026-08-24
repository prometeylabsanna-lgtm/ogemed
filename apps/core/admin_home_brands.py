"""Форма вибору брендів і фото вітрини для «Головна — Бренди»."""
from __future__ import annotations

from django import forms
from django.forms import modelformset_factory
from unfold.widgets import UnfoldAdminIntegerFieldWidget, UnfoldBooleanWidget

from apps.catalog.models import Brand
from apps.core.admin_widgets import AdminImagePreviewWidget

HOME_BRANDS_LIMIT = 3


class HomeBrandRowForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ("is_featured", "showcase_image", "sort_order")
        widgets = {
            "is_featured": UnfoldBooleanWidget(),
            "showcase_image": AdminImagePreviewWidget(),
            "sort_order": UnfoldAdminIntegerFieldWidget(),
        }
        labels = {
            "is_featured": "На головній",
            "showcase_image": "Фото на головній",
            "sort_order": "Порядок",
        }
        help_texts = {
            "showcase_image": "Якщо порожнє — візьметься фото для каталогу.",
            "is_featured": f"На вітрині показуються до {HOME_BRANDS_LIMIT} обраних.",
        }


def build_home_brands_formset(data=None, files=None):
    qs = Brand.objects.filter(is_active=True).order_by(
        "-is_featured", "sort_order", "name_uk"
    )
    FormSet = modelformset_factory(
        Brand,
        form=HomeBrandRowForm,
        extra=0,
        can_delete=False,
    )
    return FormSet(data=data, files=files, queryset=qs)


def save_home_brands_formset(formset) -> None:
    formset.save()
    # лишаємо всі is_featured як обрав адмін; вітрина сама бере [:3]
