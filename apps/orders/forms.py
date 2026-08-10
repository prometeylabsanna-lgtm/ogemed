import re

from django import forms
from django.utils.translation import gettext_lazy as _

from .models import DeliveryType, NPPointType, PaymentType

PHONE_ATTRS = {
    "data-phone-mask": "",
    "inputmode": "tel",
    "autocomplete": "tel",
}


class CheckoutForm(forms.Form):
    customer_name = forms.CharField(label=_("ПІБ"), max_length=255)
    customer_phone = forms.CharField(
        label=_("Телефон"),
        max_length=32,
        widget=forms.TextInput(attrs=PHONE_ATTRS),
    )
    customer_email = forms.EmailField(label=_("Email"), required=False)
    delivery_type = forms.ChoiceField(
        label=_("Доставка"), choices=DeliveryType.choices
    )
    np_city_ref = forms.CharField(required=False, widget=forms.HiddenInput)
    np_city_name = forms.CharField(label=_("Місто НП"), required=False, max_length=255)
    np_warehouse_ref = forms.CharField(required=False, widget=forms.HiddenInput)
    np_warehouse_name = forms.CharField(
        label=_("Відділення / поштомат"), required=False, max_length=255
    )
    np_point_type = forms.ChoiceField(
        choices=NPPointType.choices, required=False, initial=NPPointType.WAREHOUSE
    )
    courier_city = forms.CharField(label=_("Місто"), required=False, max_length=120)
    courier_street = forms.CharField(label=_("Вулиця"), required=False, max_length=255)
    courier_building = forms.CharField(label=_("Будинок"), required=False, max_length=64)
    courier_apartment = forms.CharField(label=_("Квартира"), required=False, max_length=64)
    courier_comment = forms.CharField(
        label=_("Коментар"), required=False, widget=forms.Textarea(attrs={"rows": 3})
    )
    payment_type = forms.ChoiceField(label=_("Оплата"), choices=PaymentType.choices)

    NP_FIELDS = (
        "np_city_ref",
        "np_city_name",
        "np_warehouse_ref",
        "np_warehouse_name",
        "np_point_type",
    )
    COURIER_FIELDS = (
        "courier_city",
        "courier_street",
        "courier_building",
        "courier_apartment",
        "courier_comment",
    )

    def clean_customer_phone(self):
        raw = self.cleaned_data.get("customer_phone", "")
        digits = re.sub(r"\D", "", raw or "")
        if digits.startswith("0") and len(digits) == 10:
            digits = "380" + digits[1:]
        if not re.match(r"^380\d{9}$", digits):
            raise forms.ValidationError(_("Вкажіть телефон у форматі +380XXXXXXXXX"))
        return "+" + digits

    def clean(self):
        cleaned = super().clean()
        delivery = cleaned.get("delivery_type")
        if delivery == DeliveryType.NOVA_POSHTA:
            if not cleaned.get("np_city_name") or not cleaned.get("np_warehouse_name"):
                raise forms.ValidationError(
                    _("Оберіть місто та відділення / поштомат Нової Пошти")
                )
            cleaned["np_city_ref"] = cleaned.get("np_city_ref") or "manual"
            cleaned["np_warehouse_ref"] = cleaned.get("np_warehouse_ref") or "manual"
            for field in self.COURIER_FIELDS:
                cleaned[field] = ""
        elif delivery == DeliveryType.COURIER:
            if not cleaned.get("courier_city") or not cleaned.get("courier_street"):
                raise forms.ValidationError(_("Вкажіть місто та вулицю для курʼєра"))
            for field in self.NP_FIELDS:
                cleaned[field] = ""
        return cleaned
