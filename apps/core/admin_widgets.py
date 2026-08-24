"""Віджет завантаження зображення з превʼю поточного файлу (Unfold)."""
from __future__ import annotations

from django.db import models
from unfold.widgets import UnfoldAdminImageFieldWidget

from apps.core.fields import OptimizedImageField


class AdminImagePreviewWidget(UnfoldAdminImageFieldWidget):
    """Превʼю поточного зображення над полем upload (шаблон Unfold)."""

    def __init__(self, attrs=None):
        attrs = dict(attrs or {})
        attrs.setdefault("accept", "image/*")
        super().__init__(attrs=attrs)


IMAGE_FORMFIELD_OVERRIDES = {
    models.ImageField: {"widget": AdminImagePreviewWidget},
    OptimizedImageField: {"widget": AdminImagePreviewWidget},
}
