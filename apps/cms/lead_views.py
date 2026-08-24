from django import forms
from django.http import HttpResponse
from django.utils.html import format_html, format_html_join
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from apps.core.validators import validate_email, validate_message, validate_name, validate_phone
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

    def clean_name(self):
        return validate_name(self.cleaned_data.get("name"), required=False)

    def clean_phone(self):
        return validate_phone(self.cleaned_data.get("phone"), required=True)

    def clean_email(self):
        return validate_email(self.cleaned_data.get("email"), required=False)

    def clean_message(self):
        return validate_message(self.cleaned_data.get("message"), required=False)

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
            self.add_error("name", _("Будь ласка, вкажіть ваше імʼя."))

        return cleaned


def _lead_error_response(form: LeadForm) -> HttpResponse:
    if form.non_field_errors() and "bot" in " ".join(form.non_field_errors()):
        return HttpResponse(
            format_html('<p class="lead-error">{}</p>', _("Перевірте поля форми")),
            status=422,
        )

    field_spans = []
    for field, errors in form.errors.items():
        if field == "__all__":
            continue
        for err in errors:
            field_spans.append(
                format_html(
                    '<span class="js-server-field-error" data-field-error-for="{}" hidden>{}</span>',
                    field,
                    err,
                )
            )

    summary = format_html('<p class="lead-error">{}</p>', _("Перевірте поля форми"))
    if field_spans:
        body = format_html_join("", "{}", ((span,) for span in field_spans))
        body = format_html("{}{}", body, summary)
    else:
        body = summary
    return HttpResponse(body, status=422)


@require_POST
def lead_create(request):
    form = LeadForm(request.POST)
    if not form.is_valid():
        if request.htmx:
            return _lead_error_response(form)
        return HttpResponse(_("Помилка"), status=422)

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
    return HttpResponse(format_html('<p class="lead-success">{}</p>', success))
