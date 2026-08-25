from django import forms
from django.utils.translation import gettext_lazy as _
from PIL import Image

from apps.core.admin_widgets import AdminImagePreviewWidget

from .models import ProductImage

# Рекомендація для лупи на PDP (4×). Не блокує збереження — лише попередження в адмінці.
MIN_IMAGE_SIDE = 1600


class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = "__all__"
        widgets = {
            "image": AdminImagePreviewWidget(),
        }

    def clean_image(self):
        image = self.cleaned_data.get("image")
        # старі записи не чіпаємо: перевіряємо лише щойно завантажений файл
        if not image or "image" not in self.changed_data:
            return image

        image.seek(0)
        try:
            with Image.open(image) as decoded:
                decoded.verify()
        except OSError as exc:
            raise forms.ValidationError(_("Не вдалося прочитати зображення.")) from exc
        finally:
            image.seek(0)

        return image
