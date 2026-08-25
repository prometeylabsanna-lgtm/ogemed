"""Віджет завантаження зображення з превʼю поточного файлу (Unfold)."""
from __future__ import annotations

from django.db import models
from unfold.widgets import (
    UnfoldAdminFileFieldWidget,
    UnfoldAdminImageFieldWidget,
    UnfoldAdminImageSmallFieldWidget,
)

from apps.core.fields import OptimizedImageField

# Унікальні шаблони з жорстким UK-текстом: FORM_RENDERER Unfold
# інакше бере пакетний clearable_file_input.html з {% trans %} (часто лишається EN).
_UK_FILE_INPUT = "core/widgets/clearable_file_input_uk.html"
_UK_FILE_INPUT_SMALL = "core/widgets/clearable_file_input_small_uk.html"

UnfoldAdminImageFieldWidget.template_name = _UK_FILE_INPUT
UnfoldAdminImageSmallFieldWidget.template_name = _UK_FILE_INPUT_SMALL
UnfoldAdminFileFieldWidget.template_name = _UK_FILE_INPUT_SMALL


class AdminImagePreviewWidget(UnfoldAdminImageFieldWidget):
    """Превʼю + український текст «Оберіть файл…»."""

    template_name = _UK_FILE_INPUT

    def __init__(self, attrs=None):
        attrs = dict(attrs or {})
        attrs.setdefault("accept", "image/*")
        super().__init__(attrs=attrs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        missing = False
        if value and getattr(value, "name", None):
            try:
                missing = not value.storage.exists(value.name)
            except Exception:
                missing = True
        context["widget"]["file_missing"] = missing
        return context


IMAGE_FORMFIELD_OVERRIDES = {
    models.ImageField: {"widget": AdminImagePreviewWidget},
    OptimizedImageField: {"widget": AdminImagePreviewWidget},
}
