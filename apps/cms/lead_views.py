from django import forms
from django.http import HttpResponse
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from apps.notify.services import notify_new_lead

from .models import Lead


class LeadForm(forms.ModelForm):
    website = forms.CharField(required=False, widget=forms.HiddenInput)  # honeypot
    product_label = forms.CharField(required=False, max_length=255)
    product_url = forms.CharField(required=False, max_length=500)

    class Meta:
        model = Lead
        fields = ("name", "phone", "email", "message", "lead_type")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].required = False
        self.fields["email"].required = False
        self.fields["message"].required = False

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("website"):
            raise forms.ValidationError("bot")

        lead_type = cleaned.get("lead_type") or Lead.LeadType.CALLBACK
        if lead_type == Lead.LeadType.STOCK_NOTIFY:
            if not cleaned.get("name"):
                cleaned["name"] = _("Клієнт")
            label = (cleaned.get("product_label") or "").strip()
            url = (cleaned.get("product_url") or "").strip()
            parts = [p for p in (label, url) if p]
            if parts and not cleaned.get("message"):
                cleaned["message"] = "\n".join(parts)
        elif not cleaned.get("name"):
            self.add_error("name", _("Обовʼязкове поле"))

        phone = (cleaned.get("phone") or "").strip()
        if not phone:
            self.add_error("phone", _("Обовʼязкове поле"))
        return cleaned


@require_POST
def lead_create(request):
    form = LeadForm(request.POST)
    if not form.is_valid():
        if request.htmx:
            return HttpResponse(
                f'<p class="lead-error">{_("Перевірте поля форми")}</p>',
                status=400,
            )
        return HttpResponse(_("Помилка"), status=400)

    lead = form.save(commit=False)
    lead.honeypot = form.cleaned_data.get("website", "")
    if request.user.is_authenticated:
        lead.user = request.user
    lead.save()
    notify_new_lead(lead)

    if lead.lead_type == Lead.LeadType.STOCK_NOTIFY:
        success = _("Дякуємо! Повідомимо, коли товар зʼявиться")
    else:
        success = _("Дякуємо, менеджер звʼяжеться з вами")
    return HttpResponse(f'<p class="lead-success">{success}</p>')
