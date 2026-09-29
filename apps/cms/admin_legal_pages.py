"""Єдиний редактор юридичної сторінки: CMS + CTA/замітка + секції + About."""
from __future__ import annotations

from django import forms
from django.contrib import messages
from django.contrib.admin.sites import site as default_admin_site
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from tinymce.widgets import TinyMCE
from unfold.widgets import UnfoldAdminSelectWidget, UnfoldBooleanWidget

from apps.cms.about_content import AboutContent
from apps.cms.info_page_models import InfoPageMeta, InfoPageSection
from apps.cms.legal_page_registry import LegalPageDef, get_legal_page
from apps.cms.models import CMSPage
from apps.core.admin_guidelines import get_image_hint
from apps.core.admin_site_content_widgets import (
    CmsAdminTextareaWidget,
    CmsAdminTextInputWidget,
)
from apps.core.admin_widgets import AdminImagePreviewWidget
from apps.core.models import SiteSettings

TITLE_DEFAULTS = {
    "about": ("Про нас", "О нас"),
    "contacts": ("Контакти", "Контакты"),
    "shipping": ("Доставка і оплата", "Доставка и оплата"),
    "returns": ("Повернення", "Возврат"),
    "privacy": ("Політика конфіденційності", "Политика конфиденциальности"),
    "offer": ("Публічна оферта", "Публичная оферта"),
}

ABOUT_FIELDSETS: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "Верхній банер",
        (
            "hero_visible",
            "hero_image",
            "hero_kicker_uk",
            "hero_title_uk",
            "hero_text_uk",
            "hero_kicker_ru",
            "hero_title_ru",
            "hero_text_ru",
        ),
    ),
    (
        "Історія бренду",
        (
            "history_visible",
            "history_kicker_uk",
            "history_card_1_title_uk",
            "history_card_1_body_uk",
            "history_card_2_title_uk",
            "history_card_2_body_uk",
            "history_card_3_title_uk",
            "history_card_3_body_uk",
            "history_kicker_ru",
            "history_card_1_title_ru",
            "history_card_1_body_ru",
            "history_card_2_title_ru",
            "history_card_2_body_ru",
            "history_card_3_title_ru",
            "history_card_3_body_ru",
        ),
    ),
    (
        "Філософія догляду",
        (
            "philosophy_visible",
            "philosophy_kicker_uk",
            "philosophy_title_uk",
            "philosophy_body_uk",
            "philosophy_thesis_1_title_uk",
            "philosophy_thesis_1_text_uk",
            "philosophy_thesis_2_title_uk",
            "philosophy_thesis_2_text_uk",
            "philosophy_thesis_3_title_uk",
            "philosophy_thesis_3_text_uk",
            "philosophy_thesis_4_title_uk",
            "philosophy_thesis_4_text_uk",
            "philosophy_kicker_ru",
            "philosophy_title_ru",
            "philosophy_body_ru",
            "philosophy_thesis_1_title_ru",
            "philosophy_thesis_1_text_ru",
            "philosophy_thesis_2_title_ru",
            "philosophy_thesis_2_text_ru",
            "philosophy_thesis_3_title_ru",
            "philosophy_thesis_3_text_ru",
            "philosophy_thesis_4_title_ru",
            "philosophy_thesis_4_text_ru",
        ),
    ),
    (
        "Нижній блок з кнопками",
        (
            "cta_visible",
            "cta_title_uk",
            "cta_text_uk",
            "cta_catalog_label_uk",
            "cta_contacts_label_uk",
            "cta_title_ru",
            "cta_text_ru",
            "cta_catalog_label_ru",
            "cta_contacts_label_ru",
        ),
    ),
)

ABOUT_FIELDS = tuple(f for _, fields in ABOUT_FIELDSETS for f in fields)

META_FIELDS = (
    "cta_title_uk",
    "cta_text_uk",
    "cta_title_ru",
    "cta_text_ru",
    "note_title_uk",
    "note_steps_uk",
    "note_text_uk",
    "note_title_ru",
    "note_steps_ru",
    "note_text_ru",
)

FOP_FIELDS = (
    "fop_recipient_name",
    "fop_iban",
    "fop_card_number",
    "fop_edrpou",
)


def _lang_wrap_class(name: str) -> str:
    if name.endswith("_ru") or name.endswith("_ru_id"):
        return "cms-lang-ru"
    if name.endswith("_uk") or name.endswith("_uk_id"):
        return "cms-lang-uk"
    return ""


class LegalCMSPageForm(forms.ModelForm):
    class Meta:
        model = CMSPage
        fields = ("title_uk", "body_uk", "title_ru", "body_ru", "is_published")
        widgets = {
            "title_uk": CmsAdminTextInputWidget(),
            "title_ru": CmsAdminTextInputWidget(),
            "body_uk": TinyMCE(attrs={"cols": 80, "rows": 10}),
            "body_ru": TinyMCE(attrs={"cols": 80, "rows": 10}),
            "is_published": UnfoldBooleanWidget(),
        }


class LegalInfoMetaForm(forms.ModelForm):
    class Meta:
        model = InfoPageMeta
        fields = META_FIELDS
        widgets = {
            "cta_title_uk": CmsAdminTextInputWidget(),
            "cta_title_ru": CmsAdminTextInputWidget(),
            "cta_text_uk": CmsAdminTextareaWidget(attrs={"rows": 3}),
            "cta_text_ru": CmsAdminTextareaWidget(attrs={"rows": 3}),
            "note_title_uk": CmsAdminTextInputWidget(),
            "note_title_ru": CmsAdminTextInputWidget(),
            "note_steps_uk": CmsAdminTextareaWidget(attrs={"rows": 4}),
            "note_steps_ru": CmsAdminTextareaWidget(attrs={"rows": 4}),
            "note_text_uk": CmsAdminTextareaWidget(attrs={"rows": 3}),
            "note_text_ru": CmsAdminTextareaWidget(attrs={"rows": 3}),
        }


class LegalFopForm(forms.ModelForm):
    """Реквізити ФОП — ті самі SiteSettings, що для checkout / thank-you."""

    class Meta:
        model = SiteSettings
        fields = FOP_FIELDS
        widgets = {name: CmsAdminTextInputWidget() for name in FOP_FIELDS}


class LegalAboutForm(forms.ModelForm):
    class Meta:
        model = AboutContent
        fields = ABOUT_FIELDS
        widgets = {
            "hero_image": AdminImagePreviewWidget(),
            "hero_visible": UnfoldBooleanWidget(),
            "history_visible": UnfoldBooleanWidget(),
            "philosophy_visible": UnfoldBooleanWidget(),
            "cta_visible": UnfoldBooleanWidget(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "hero_image" in self.fields:
            self.fields["hero_image"].help_text = get_image_hint("about_hero")
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.Textarea) and not isinstance(
                field.widget, TinyMCE
            ):
                field.widget = CmsAdminTextareaWidget(
                    attrs={"rows": 3, **(field.widget.attrs or {})}
                )
            elif isinstance(field.widget, forms.TextInput):
                field.widget = CmsAdminTextInputWidget(attrs=field.widget.attrs)


class LegalSectionForm(forms.ModelForm):
    class Meta:
        model = InfoPageSection
        fields = (
            "layout",
            "heading_uk",
            "subheading_uk",
            "body_uk",
            "heading_ru",
            "subheading_ru",
            "body_ru",
            "sort_order",
            "is_active",
        )
        widgets = {
            "layout": UnfoldAdminSelectWidget(),
            "heading_uk": CmsAdminTextInputWidget(),
            "heading_ru": CmsAdminTextInputWidget(),
            "subheading_uk": CmsAdminTextInputWidget(),
            "subheading_ru": CmsAdminTextInputWidget(),
            "body_uk": TinyMCE(attrs={"cols": 80, "rows": 8}),
            "body_ru": TinyMCE(attrs={"cols": 80, "rows": 8}),
            "is_active": UnfoldBooleanWidget(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Порожній extra/JS-рядок не блокує збереження
        if "heading_uk" in self.fields:
            self.fields["heading_uk"].required = False

    def clean(self):
        cleaned = super().clean()
        heading = (cleaned.get("heading_uk") or "").strip()
        body = (cleaned.get("body_uk") or "").strip()
        if not self.instance.pk and not heading and not body:
            cleaned["DELETE"] = True
        elif not heading and self.instance.pk:
            self.add_error("heading_uk", "Обовʼязкове поле.")
        return cleaned


def build_sections_formset(page_key: str, data=None):
    FormSet = forms.modelformset_factory(
        InfoPageSection,
        form=LegalSectionForm,
        extra=0,
        can_delete=True,
    )
    qs = InfoPageSection.objects.filter(page_key=page_key).order_by(
        "sort_order", "id"
    )
    return FormSet(data, queryset=qs, prefix="sections")


def get_or_create_cms_page(defn: LegalPageDef) -> CMSPage:
    page = CMSPage.objects.filter(page_key=defn.key).first()
    if page:
        return page
    page = CMSPage.objects.filter(slug=defn.slug_default).first()
    if page:
        if not page.page_key:
            page.page_key = defn.key
            page.save(update_fields=["page_key", "updated_at"])
        return page
    title_uk, title_ru = TITLE_DEFAULTS.get(defn.key, (defn.title, defn.title))
    return CMSPage.objects.create(
        slug=defn.slug_default,
        page_key=defn.key,
        title_uk=title_uk,
        title_ru=title_ru,
        is_published=True,
        sort_order={"about": 10, "contacts": 20, "shipping": 30, "returns": 40, "privacy": 50, "offer": 60}.get(
            defn.key, 100
        ),
    )


def get_or_create_meta(page_key: str) -> InfoPageMeta:
    meta, _ = InfoPageMeta.objects.get_or_create(page_key=page_key)
    return meta


def _bound_fields(form: forms.BaseForm, names: tuple[str, ...]) -> list:
    return [form[name] for name in names if name in form.fields]


def _field_wrap_class(field) -> str:
    return _lang_wrap_class(field.name)


def legal_page_edit_view(request, page_key: str, *, model_admin=None):
    try:
        defn = get_legal_page(page_key)
    except KeyError as exc:
        raise Http404 from exc

    cms_page = get_or_create_cms_page(defn)
    about_obj = AboutContent.load() if defn.has_about else None
    meta_obj = get_or_create_meta(defn.key) if defn.has_meta else None
    site_obj = SiteSettings.load() if defn.has_fop else None

    page_form = None
    about_form = None
    meta_form = None
    fop_form = None
    sections_formset = None

    if request.method == "POST":
        page_form = LegalCMSPageForm(request.POST, instance=cms_page)
        ok = page_form.is_valid()
        if defn.has_about:
            about_form = LegalAboutForm(
                request.POST, request.FILES, instance=about_obj
            )
            ok = ok and about_form.is_valid()
        if defn.has_meta:
            meta_form = LegalInfoMetaForm(request.POST, instance=meta_obj)
            ok = ok and meta_form.is_valid()
        if defn.has_fop:
            fop_form = LegalFopForm(request.POST, instance=site_obj)
            ok = ok and fop_form.is_valid()
        if defn.has_sections:
            sections_formset = build_sections_formset(defn.key, request.POST)
            ok = ok and sections_formset.is_valid()
        if ok:
            page_form.save()
            if about_form is not None:
                about_form.save()
            if meta_form is not None:
                meta_form.save()
            if fop_form is not None:
                fop_form.save()
            if sections_formset is not None:
                instances = sections_formset.save(commit=False)
                for obj in instances:
                    obj.page_key = defn.key
                    obj.save()
                for obj in sections_formset.deleted_objects:
                    obj.delete()
                sections_formset.save_m2m()
            messages.success(request, f"«{defn.title}» збережено.")
            return HttpResponseRedirect(
                reverse(f"admin:cms_{defn.model_name}_changelist")
            )
    else:
        page_form = LegalCMSPageForm(instance=cms_page)
        if defn.has_about:
            about_form = LegalAboutForm(instance=about_obj)
        if defn.has_meta:
            meta_form = LegalInfoMetaForm(instance=meta_obj)
        if defn.has_fop:
            fop_form = LegalFopForm(instance=site_obj)
        if defn.has_sections:
            sections_formset = build_sections_formset(defn.key)

    fieldsets: list[tuple[str, list]] = [
        (
            "Заголовок і текст сторінки",
            _bound_fields(
                page_form, ("title_uk", "body_uk", "title_ru", "body_ru", "is_published")
            ),
        ),
    ]
    if about_form is not None:
        for title, names in ABOUT_FIELDSETS:
            fields = _bound_fields(about_form, names)
            if fields:
                fieldsets.append((title, fields))
    if fop_form is not None:
        fieldsets.append(
            (
                "Реквізити ФОП (оплата на картку / IBAN)",
                _bound_fields(fop_form, FOP_FIELDS),
            )
        )
    if meta_form is not None:
        fieldsets.append(
            (
                "Форма CTA",
                _bound_fields(
                    meta_form,
                    ("cta_title_uk", "cta_text_uk", "cta_title_ru", "cta_text_ru"),
                ),
            )
        )
        fieldsets.append(
            (
                "Бічна замітка",
                _bound_fields(
                    meta_form,
                    (
                        "note_title_uk",
                        "note_steps_uk",
                        "note_text_uk",
                        "note_title_ru",
                        "note_steps_ru",
                        "note_text_ru",
                    ),
                ),
            )
        )

    opts = model_admin.model._meta if model_admin else CMSPage._meta
    media = page_form.media
    if about_form is not None:
        media = media + about_form.media
    if meta_form is not None:
        media = media + meta_form.media
    if fop_form is not None:
        media = media + fop_form.media
    if sections_formset is not None:
        media = media + sections_formset.media

    context = {
        **default_admin_site.each_context(request),
        "title": defn.title,
        "defn": defn,
        "page_form": page_form,
        "about_form": about_form,
        "meta_form": meta_form,
        "fop_form": fop_form,
        "sections_formset": sections_formset,
        "fieldsets": fieldsets,
        "field_wrap_class": _field_wrap_class,
        "preview_url": defn.preview_path,
        "breadcrumb": (("Юридичні сторінки", None), (defn.title, None)),
        "opts": opts,
        "media": media,
        "has_view_permission": True,
        "add": False,
        "change": True,
        "is_popup": False,
        "save_as": False,
        "show_save": True,
        "show_save_and_continue": False,
        "show_save_and_add_another": False,
        "show_delete": False,
    }
    return render(request, "admin/cms/legal_page_edit.html", context)
