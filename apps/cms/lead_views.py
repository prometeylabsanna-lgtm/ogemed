from django import forms
from django.http import HttpResponse
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from apps.notify.services import notify_new_lead

from .models import Lead


class LeadForm(forms.ModelForm):
    website = forms.CharField(required=False, widget=forms.HiddenInput)  # honeypot

    class Meta:
        model = Lead
        fields = ("name", "phone", "email", "message", "lead_type")

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("website"):
            raise forms.ValidationError("bot")
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

    success_html = f'<p class="lead-success">{_("Дякуємо, менеджер звʼяжеться з вами")}</p>'
    return HttpResponse(success_html)
