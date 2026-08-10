"""Реєстр міток товару (чекбокси в адмінці → рядок іконок у картці товару).

Тільки дані: жодних імпортів моделей, тому модуль вільно підключається будь-де.
Щоб додати нову мітку: додати запис у PRODUCT_LABELS + BooleanField з такою ж
назвою в Product + маску static/img/labels/<icon>.png і правило в label_icons.css.
Значення icon — назва файлу маски без розширення, slug — значення ?label= в URL.
"""
from dataclasses import dataclass

from django.utils.translation import gettext_lazy as _


@dataclass(frozen=True)
class ProductLabel:
    field: str
    icon: str
    title: str

    @property
    def slug(self) -> str:
        return self.field.removeprefix("label_").replace("_", "-")


PRODUCT_LABELS: tuple[ProductLabel, ...] = (
    ProductLabel("label_fragrance_free", "perfume_off", _("Без ароматизаторів")),
    ProductLabel("label_vegan", "branch", _("Веган-формула")),
    ProductLabel("label_derma_tested", "face_check", _("Дерматологічно протестовано")),
    ProductLabel("label_gentle", "leaf_soft", _("Делікатна формула")),
    ProductLabel("label_hypoallergenic", "hand_drop", _("Гіпоалергенно")),
    ProductLabel("label_paraben_free", "flask_off", _("Без парабенів")),
    ProductLabel("label_cruelty_free", "bunny_off", _("Без тестів на тваринах")),
    ProductLabel("label_cleansing", "face_care", _("Очищення")),
)

LABEL_FIELDS: tuple[str, ...] = tuple(label.field for label in PRODUCT_LABELS)

LABELS_BY_SLUG: dict[str, ProductLabel] = {label.slug: label for label in PRODUCT_LABELS}


def active_labels(product) -> list[ProductLabel]:
    return [label for label in PRODUCT_LABELS if getattr(product, label.field, False)]


def label_by_slug(slug: str | None) -> ProductLabel | None:
    """Мітка за значенням ?label= (None, якщо слаг невідомий — фільтр ігнорується)."""
    return LABELS_BY_SLUG.get(slug or "")
