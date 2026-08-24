"""CMS section form + view (UA/RU через modeltranslation)."""
from __future__ import annotations

from django import forms
from django.contrib import messages
from django.contrib.admin.sites import site as default_admin_site
from django.core.cache import cache
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from unfold.widgets import UnfoldBooleanWidget

from apps.core.admin_widgets import AdminImagePreviewWidget

from apps.core.admin_guidelines import get_image_hint, get_text_limit_hint
from apps.core.admin_hero_slides import build_hero_slide_formset
from apps.core.admin_site_content_widgets import (
    CmsAdminTextareaWidget,
    CmsAdminTextInputWidget,
)
from apps.core.block_defaults import (
    BLOCK_CONTENT_TYPES,
    INLINE_KEYS,
    MULTILINE_KEYS,
    default_pair,
    is_visibility_key,
)
from apps.core.context_processors import SITE_BLOCKS_CACHE_KEY
from apps.core.models import SiteBlock, SiteSettings
from apps.core.site_content_registry import (
    ContentSection,
    get_block_field_label,
    get_section,
    iter_section_blocks,
)

SECTION_VISIBLE_FIELD = "section_visible"
LANGS = ("uk", "ru")
HEADER_BRAND_FIELDS = ("logo", "phone")


class HeaderBrandForm(forms.ModelForm):
    """Логотип і телефон шапки = поля SiteSettings (спільні з «Налаштування сайту»)."""

    class Meta:
        model = SiteSettings
        fields = HEADER_BRAND_FIELDS
        widgets = {
            "logo": AdminImagePreviewWidget(),
            "phone": CmsAdminTextInputWidget(),
        }


def block_field_name(page: str, key: str, suffix: str) -> str:
    return f"block__{page}__{key}__{suffix}"


def _block_content_type(page: str, key: str) -> str:
    return BLOCK_CONTENT_TYPES.get((page, key), SiteBlock.ContentType.TEXT)


def _text_widget(key: str):
    if key in INLINE_KEYS:
        return CmsAdminTextInputWidget()
    if key in MULTILINE_KEYS:
        return CmsAdminTextareaWidget(attrs={"rows": 4})
    return CmsAdminTextareaWidget(attrs={"rows": 2})


def _get_lang_text(block: SiteBlock, lang: str) -> str:
    attr = f"text_html_{lang}"
    if hasattr(block, attr):
        return getattr(block, attr) or ""
    return block.text_html or ""


def _set_lang_text(block: SiteBlock, lang: str, value: str) -> None:
    attr = f"text_html_{lang}"
    if hasattr(block, attr):
        setattr(block, attr, value)
    if lang == "uk":
        block.text_html = value


def load_section_blocks(section: ContentSection) -> dict[tuple[str, str], SiteBlock]:
    blocks: dict[tuple[str, str], SiteBlock] = {}
    for page, key in iter_section_blocks(section):
        content_type = _block_content_type(page, key)
        uk_default, ru_default = default_pair(page, key)
        if is_visibility_key(key):
            uk_default = uk_default or "1"
            ru_default = ru_default or uk_default
        block, created = SiteBlock.objects.get_or_create(
            page=page,
            key=key,
            defaults={
                "label": get_block_field_label(page, key),
                "content_type": content_type,
                "text_html": uk_default,
                "sort_order": 0,
                "is_active": True,
            },
        )
        if created:
            _set_lang_text(block, "uk", uk_default)
            _set_lang_text(block, "ru", ru_default)
            block.save()
        blocks[(page, key)] = block
    return blocks


class SitePageContentForm(forms.Form):
    def __init__(
        self,
        section: ContentSection,
        blocks: dict[tuple[str, str], SiteBlock],
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.section = section
        self.blocks = blocks

        if section.visibility_key:
            page, key = self._visibility_page_key(section)
            block = blocks[(page, key)]
            initial = _get_lang_text(block, "uk").strip() in {"1", "true", "True"}
            self.fields[SECTION_VISIBLE_FIELD] = forms.BooleanField(
                label="Показувати секцію на сайті",
                required=False,
                initial=initial,
                widget=UnfoldBooleanWidget(),
            )

        for page, key in section.blocks:
            self._add_block_fields(blocks[(page, key)])

    def _visibility_page_key(self, section: ContentSection) -> tuple[str, str]:
        for page, key in iter_section_blocks(section):
            if key == section.visibility_key:
                return page, key
        raise KeyError(section.visibility_key)

    def _add_block_fields(self, block: SiteBlock) -> None:
        page, key = block.page, block.key
        label = get_block_field_label(page, key)

        if is_visibility_key(key) and key != self.section.visibility_key:
            initial = _get_lang_text(block, "uk").strip() in {"1", "true", "True"}
            self.fields[block_field_name(page, key, "visible")] = forms.BooleanField(
                label=label,
                required=False,
                initial=initial,
                widget=UnfoldBooleanWidget(),
            )
            return

        if block.content_type == SiteBlock.ContentType.IMAGE:
            hint = get_image_hint(key) or get_image_hint("block_image")
            current = f"Поточне: {block.image.name}. " if block.image else ""
            self.fields[block_field_name(page, key, "image")] = forms.ImageField(
                label=label,
                required=False,
                widget=AdminImagePreviewWidget(),
                help_text=current + hint,
            )
            return

        # TEXT / URL — дві мови
        char_hint = get_text_limit_hint(key)
        for lang, lang_label in (("uk", "UA"), ("ru", "RU")):
            self.fields[block_field_name(page, key, f"text_html_{lang}")] = forms.CharField(
                label=f"{label} [{lang_label}]",
                initial=_get_lang_text(block, lang),
                required=False,
                widget=_text_widget(key),
                help_text=char_hint if lang == "uk" else "",
            )

    def save(self) -> None:
        if SECTION_VISIBLE_FIELD in self.fields:
            page, key = self._visibility_page_key(self.section)
            block = self.blocks[(page, key)]
            flag = "1" if self.cleaned_data.get(SECTION_VISIBLE_FIELD) else "0"
            _set_lang_text(block, "uk", flag)
            _set_lang_text(block, "ru", flag)
            block.is_active = True
            block.save()

        for block in self.blocks.values():
            page, key = block.page, block.key
            if key == self.section.visibility_key:
                continue
            if is_visibility_key(key):
                flag = "1" if self.cleaned_data.get(
                    block_field_name(page, key, "visible")
                ) else "0"
                _set_lang_text(block, "uk", flag)
                _set_lang_text(block, "ru", flag)
                block.is_active = True
                block.save()
                continue

            block.is_active = True
            if block.content_type == SiteBlock.ContentType.IMAGE:
                uploaded = self.cleaned_data.get(block_field_name(page, key, "image"))
                if uploaded:
                    block.image = uploaded
            else:
                for lang in LANGS:
                    value = self.cleaned_data.get(
                        block_field_name(page, key, f"text_html_{lang}"),
                        "",
                    )
                    _set_lang_text(block, lang, (value or "").strip())
            block.save()

        cache.delete(SITE_BLOCKS_CACHE_KEY)


def _field_names_for_key(form: SitePageContentForm, page: str, key: str) -> list[str]:
    block = form.blocks.get((page, key))
    if block is None:
        return []
    if is_visibility_key(key):
        return [block_field_name(page, key, "visible")]
    if block.content_type == SiteBlock.ContentType.IMAGE:
        return [block_field_name(page, key, "image")]
    return [
        block_field_name(page, key, "text_html_uk"),
        block_field_name(page, key, "text_html_ru"),
    ]


def _bound_fields_for_keys(
    form: SitePageContentForm,
    section: ContentSection,
    keys: tuple[str, ...],
) -> list:
    fields = []
    page_keys = {key: page for page, key in section.blocks}
    for key in keys:
        page = page_keys[key]
        for name in _field_names_for_key(form, page, key):
            if name in form.fields:
                fields.append(form[name])
    return fields


def _section_fieldsets(
    form: SitePageContentForm,
    section: ContentSection,
    *,
    header_form: HeaderBrandForm | None = None,
) -> list:
    fieldsets: list = []
    if header_form is not None:
        fieldsets.append(
            (
                "Логотип і телефон",
                [header_form[name] for name in HEADER_BRAND_FIELDS if name in header_form.fields],
            )
        )
    if SECTION_VISIBLE_FIELD in form.fields:
        fieldsets.append(("Видимість", [form[SECTION_VISIBLE_FIELD]]))
    if section.field_groups:
        for group in section.field_groups:
            fields = _bound_fields_for_keys(form, section, group.block_keys)
            if fields:
                fieldsets.append((group.title, fields))
    return fieldsets


def _section_admin_change_url(section: ContentSection) -> str:
    return reverse(
        f"admin:core_{section.admin_model_name}_change",
        args=[SiteSettings.load().pk],
    )


def site_content_section_view(
    request,
    page_slug: str,
    section_slug: str,
    *,
    model_admin=None,
):
    try:
        section = get_section(page_slug, section_slug)
    except KeyError as exc:
        raise Http404 from exc

    blocks = load_section_blocks(section)
    use_hero_slides = section.slug == "hero"
    use_header_brand = section.slug == "header"
    slides_formset = None
    header_form = None
    settings_obj = SiteSettings.load() if use_header_brand else None

    if request.method == "POST":
        form = SitePageContentForm(section, blocks, request.POST, request.FILES)
        if use_hero_slides:
            slides_formset = build_hero_slide_formset(request.POST, request.FILES)
        if use_header_brand:
            header_form = HeaderBrandForm(
                request.POST, request.FILES, instance=settings_obj
            )
        forms_ok = form.is_valid()
        if use_hero_slides:
            forms_ok = forms_ok and slides_formset.is_valid()
        if use_header_brand:
            forms_ok = forms_ok and header_form.is_valid()
        if forms_ok:
            form.save()
            if slides_formset is not None:
                slides_formset.save()
            if header_form is not None:
                header_form.save()
            messages.success(
                request,
                f"«{section.sidebar_title or section.title}» збережено.",
            )
            return HttpResponseRedirect(_section_admin_change_url(section))
    else:
        form = SitePageContentForm(section, blocks)
        if use_hero_slides:
            slides_formset = build_hero_slide_formset()
        if use_header_brand:
            header_form = HeaderBrandForm(instance=settings_obj)

    opts = model_admin.model._meta if model_admin else SiteBlock._meta
    context = {
        **default_admin_site.each_context(request),
        "form": form,
        "header_form": header_form,
        "section": section,
        "fieldsets": _section_fieldsets(form, section, header_form=header_form),
        "slides_formset": slides_formset,
        "preview_url": section.preview_url,
        "title": section.sidebar_title or section.title,
        "breadcrumb": (
            ("Контент сторінок", None),
            (section.sidebar_title or section.title, None),
        ),
        "opts": opts,
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
    return render(request, "admin/core/site_content_page.html", context)
