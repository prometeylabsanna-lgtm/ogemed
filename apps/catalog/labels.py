"""Реєстр міток товару (чекбокси в адмінці → рядок іконок у картці товару).

Тільки дані: жодних імпортів моделей на рівні модуля (окрім lazy в icon_url).
Щоб додати нову мітку: додати запис у PRODUCT_LABELS + BooleanField з такою ж
назвою в Product + маску static/img/labels/<icon>.png.
Значення icon — назва файлу маски без розширення, slug — значення ?label= в URL.
"""
from __future__ import annotations

from dataclasses import dataclass

from django.templatetags.static import static
from django.utils.translation import get_language, gettext_lazy as _


@dataclass(frozen=True)
class ProductLabel:
    field: str
    icon: str
    title: str

    @property
    def slug(self) -> str:
        return self.field.removeprefix("label_").replace("_", "-")

    @property
    def icon_url(self) -> str:
        return label_icon_url(self.icon)

    def display_title(self) -> str:
        """Підпис з LabelIcon (UK/RU), інакше дефолт з реєстру."""
        try:
            from apps.catalog.models import LabelIcon

            obj = (
                LabelIcon.objects.filter(key=self.icon)
                .only("title_uk", "title_ru")
                .first()
            )
        except Exception:
            obj = None
        if obj is not None:
            lang = (get_language() or "uk")[:2]
            if lang == "ru" and obj.title_ru:
                return obj.title_ru
            if obj.title_uk:
                return obj.title_uk
        return str(self.title)


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

# Дефолтні RU-підписи для seed LabelIcon (адмін може змінити).
LABEL_TITLE_RU: dict[str, str] = {
    "perfume_off": "Без ароматизаторов",
    "branch": "Веган-формула",
    "face_check": "Дерматологически протестировано",
    "leaf_soft": "Деликатная формула",
    "hand_drop": "Гипоаллергенно",
    "flask_off": "Без парабенов",
    "bunny_off": "Без тестов на животных",
    "face_care": "Очищение",
}

LABEL_FIELDS: tuple[str, ...] = tuple(label.field for label in PRODUCT_LABELS)

LABELS_BY_FIELD: dict[str, ProductLabel] = {
    label.field: label for label in PRODUCT_LABELS
}
LABELS_BY_SLUG: dict[str, ProductLabel] = {label.slug: label for label in PRODUCT_LABELS}


def label_icon_url(icon: str) -> str:
    """URL маски: media-override або static/img/labels/<icon>.png."""
    try:
        from apps.catalog.models import LabelIcon

        obj = (
            LabelIcon.objects.filter(key=icon)
            .exclude(image="")
            .only("image")
            .first()
        )
        if obj and obj.image:
            return obj.image.url
    except Exception:
        pass
    return static(f"img/labels/{icon}.png")


@dataclass(frozen=True)
class ResolvedProductLabel:
    field: str
    icon: str
    title: str
    slug: str
    icon_url: str


def active_labels(product) -> list[ResolvedProductLabel]:
    result: list[ResolvedProductLabel] = []
    for label in PRODUCT_LABELS:
        if not getattr(product, label.field, False):
            continue
        result.append(
            ResolvedProductLabel(
                field=label.field,
                icon=label.icon,
                title=label.display_title(),
                slug=label.slug,
                icon_url=label.icon_url,
            )
        )
    return result


def label_by_slug(slug: str | None) -> ProductLabel | None:
    """Мітка за значенням ?label= (None, якщо слаг невідомий — фільтр ігнорується)."""
    return LABELS_BY_SLUG.get(slug or "")
