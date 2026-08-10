from django import forms
from django.utils.translation import gettext_lazy as _
from PIL import Image

from .models import ProductImage

# Фото на сторінці товару збільшується до 4×, тому дрібний файл дає мутну лупу
MIN_IMAGE_SIDE = 1600


class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = "__all__"

    def clean_image(self):
        image = self.cleaned_data.get("image")
        # старі записи не блокуємо: перевіряємо лише щойно завантажений файл
        if not image or "image" not in self.changed_data:
            return image

        image.seek(0)
        try:
            with Image.open(image) as decoded:
                width, height = decoded.size
        except OSError as exc:
            raise forms.ValidationError(_("Не вдалося прочитати зображення.")) from exc
        finally:
            image.seek(0)

        if max(width, height) < MIN_IMAGE_SIDE:
            raise forms.ValidationError(
                _(
                    "Фото %(width)s×%(height)spx замале. Потрібно від %(min)spx "
                    "по довгій стороні, інакше збільшення на сторінці товару буде розмитим."
                ),
                params={"width": width, "height": height, "min": MIN_IMAGE_SIDE},
            )
        return image
