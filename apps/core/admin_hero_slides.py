"""HeroSlide formset для CMS-секції Hero (модель apps.cms.HeroSlide)."""
from __future__ import annotations

from django import forms
from django.forms import BaseModelFormSet, modelformset_factory
from unfold.widgets import UnfoldAdminFileFieldWidget, UnfoldBooleanWidget

from apps.cms.models import HeroSlide
from apps.core.admin_guidelines import get_image_hint
from apps.core.admin_site_content_widgets import CmsAdminTextInputWidget

_HERO_IMAGE_HINT = get_image_hint("hero")


class HeroSlideForm(forms.ModelForm):
    class Meta:
        model = HeroSlide
        fields = (
            "image",
            "title_uk",
            "title_ru",
            "subtitle_uk",
            "subtitle_ru",
            "cta_label_uk",
            "cta_label_ru",
            "cta_url",
            "sort_order",
            "is_active",
        )
        widgets = {
            "image": UnfoldAdminFileFieldWidget(),
            "title_uk": CmsAdminTextInputWidget(),
            "title_ru": CmsAdminTextInputWidget(),
            "subtitle_uk": CmsAdminTextInputWidget(),
            "subtitle_ru": CmsAdminTextInputWidget(),
            "cta_label_uk": CmsAdminTextInputWidget(),
            "cta_label_ru": CmsAdminTextInputWidget(),
            "cta_url": CmsAdminTextInputWidget(),
            "sort_order": forms.HiddenInput(),
            "is_active": UnfoldBooleanWidget(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["image"].required = False
        self.fields["image"].help_text = _HERO_IMAGE_HINT
        for name in (
            "title_uk",
            "title_ru",
            "subtitle_uk",
            "subtitle_ru",
            "cta_label_uk",
            "cta_label_ru",
            "cta_url",
        ):
            self.fields[name].required = False
        self.fields["is_active"].required = False
        if not self.instance.pk:
            self.fields["is_active"].initial = True

    def _has_content(self, cleaned: dict) -> bool:
        if cleaned.get("image") or (self.instance.pk and self.instance.image):
            return True
        return bool((cleaned.get("title_uk") or "").strip())

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("DELETE"):
            return cleaned
        if not self._has_content(cleaned):
            return cleaned
        if not (cleaned.get("title_uk") or "").strip() and not (
            self.instance.pk and self.instance.title_uk
        ):
            self.add_error("title_uk", "Вкажіть заголовок (UK).")
        return cleaned


class HeroSlideBaseFormSet(BaseModelFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return
        order = 0
        for form in self.forms:
            if not hasattr(form, "cleaned_data") or not form.cleaned_data:
                continue
            if form.cleaned_data.get("DELETE"):
                continue
            if not form._has_content(form.cleaned_data):
                continue
            form.cleaned_data["sort_order"] = order
            form.instance.sort_order = order
            order += 1

    def save(self, commit=True):
        if not commit:
            return super().save(commit=False)
        saved = []
        for form in self.forms:
            if not hasattr(form, "cleaned_data") or not form.cleaned_data:
                continue
            if form.cleaned_data.get("DELETE"):
                if form.instance.pk:
                    form.instance.delete()
                continue
            if not form._has_content(form.cleaned_data):
                continue
            saved.append(form.save(commit=True))
        return saved


HeroSlideFormSet = modelformset_factory(
    HeroSlide,
    form=HeroSlideForm,
    formset=HeroSlideBaseFormSet,
    extra=1,
    can_delete=True,
)


def build_hero_slide_formset(data=None, files=None) -> HeroSlideFormSet:
    queryset = HeroSlide.objects.all().order_by("sort_order", "id")
    if data is None and files is None:
        return HeroSlideFormSet(queryset=queryset, prefix="hero_slides")
    return HeroSlideFormSet(data, files, queryset=queryset, prefix="hero_slides")
