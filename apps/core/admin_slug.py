"""Авто-slug + захист від випадкового редагування в адмінці."""
from __future__ import annotations

from django import forms
from django.utils.text import slugify
from unfold.widgets import UnfoldBooleanWidget

SLUG_LOCK_JS = ("js/admin/slug_lock.js",)
SLUG_LOCK_CSS = ("css/admin/slug_lock.css",)

# Мінімальна транслітерація UA/RU → латиниця для ASCII-URL
_TRANSLIT = str.maketrans(
    {
        "а": "a",
        "б": "b",
        "в": "v",
        "г": "h",
        "ґ": "g",
        "д": "d",
        "е": "e",
        "є": "ye",
        "ж": "zh",
        "з": "z",
        "и": "y",
        "і": "i",
        "ї": "yi",
        "й": "y",
        "к": "k",
        "л": "l",
        "м": "m",
        "н": "n",
        "о": "o",
        "п": "p",
        "р": "r",
        "с": "s",
        "т": "t",
        "у": "u",
        "ф": "f",
        "х": "kh",
        "ц": "ts",
        "ч": "ch",
        "ш": "sh",
        "щ": "shch",
        "ь": "",
        "ю": "yu",
        "я": "ya",
        "ы": "y",
        "э": "e",
        "ё": "yo",
        "ъ": "",
    }
)


def _ascii_slug_base(source: str, fallback: str) -> str:
    text = (source or "").strip().lower()
    if text:
        text = text.translate(_TRANSLIT)
    base = slugify(text) or slugify(source or "") or fallback
    return base


def unique_slug(
    model,
    source: str,
    *,
    pk=None,
    fallback: str = "item",
    max_length: int = 80,
    scope_filter: dict | None = None,
    slug_field: str = "slug",
) -> str:
    """Унікальний slug з назви; за наявності pk — суфікс -{pk}."""
    base = _ascii_slug_base(source, fallback)
    qs = model.objects.all()
    if scope_filter:
        qs = qs.filter(**scope_filter)
    if pk:
        qs = qs.exclude(pk=pk)
        suffix = f"-{pk}"
        stem = base[: max(1, max_length - len(suffix))]
        return f"{stem}{suffix}"

    slug = base[:max_length]
    n = 2
    while qs.filter(**{slug_field: slug}).exists():
        suffix = f"-{n}"
        slug = f"{base[: max(1, max_length - len(suffix))]}{suffix}"
        n += 1
    return slug


def _inject_slug_unlock(fieldsets: list, slug_field: str) -> list:
    out = []
    for title, opts in fieldsets:
        opts = dict(opts)
        fields = opts.get("fields")
        if not fields:
            out.append((title, opts))
            continue
        new_fields: list = []
        for item in fields:
            new_fields.append(item)
            if item == slug_field:
                new_fields.append("slug_unlock")
            elif isinstance(item, (list, tuple)) and slug_field in item:
                new_fields.append("slug_unlock")
        opts["fields"] = tuple(new_fields)
        out.append((title, opts))
    return out


class SlugLockAdminMixin:
    """
    Slug генерується з slug_source_field і readonly, поки не увімкнути
    «Дозволити редагувати slug».
    """

    slug_source_field = "name_uk"
    slug_field_name = "slug"
    slug_fallback = "item"
    slug_max_length = 80
    # callable(instance, cleaned_data) -> dict | None
    slug_scope_from_instance = None

    class Media:
        js = SLUG_LOCK_JS
        css = {"all": SLUG_LOCK_CSS}

    def get_prepopulated_fields(self, request, obj=None):
        return {}

    def get_form(self, request, obj=None, **kwargs):
        BaseForm = super().get_form(request, obj, **kwargs)
        mixin = self

        class FormWithSlugLock(BaseForm):
            slug_unlock = forms.BooleanField(
                label="Дозволити редагувати slug",
                required=False,
                widget=UnfoldBooleanWidget(),
                help_text=(
                    "За замовчуванням slug створюється з назви і захищений. "
                    "Увімкніть лише якщо треба змінити URL вручну."
                ),
            )

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                slug_name = mixin.slug_field_name
                if slug_name not in self.fields:
                    return
                field = self.fields[slug_name]
                field.required = False
                field.help_text = (
                    "Генерується автоматично з назви. "
                    "Редагувати можна лише з галочкою нижче."
                )
                field.widget.attrs["data-slug-lock-input"] = "1"
                css = (field.widget.attrs.get("class") or "").strip()
                if "slug-lock-input" not in css.split():
                    field.widget.attrs["class"] = f"{css} slug-lock-input".strip()
                if not (self.data and self.data.get("slug_unlock")):
                    field.widget.attrs["readonly"] = True

            def clean(self):
                cleaned = super().clean()
                if mixin.slug_field_name not in self.fields:
                    return cleaned
                unlock = bool(cleaned.get("slug_unlock"))
                source = (
                    cleaned.get(mixin.slug_source_field)
                    or getattr(self.instance, mixin.slug_source_field, "")
                    or ""
                )
                current = (cleaned.get(mixin.slug_field_name) or "").strip()
                if unlock and current:
                    self.instance._auto_slug = False
                    cleaned[mixin.slug_field_name] = current
                    return cleaned
                self.instance._auto_slug = True
                scope = None
                if callable(mixin.slug_scope_from_instance):
                    scope = mixin.slug_scope_from_instance(self.instance, cleaned)
                cleaned[mixin.slug_field_name] = unique_slug(
                    self._meta.model,
                    source,
                    pk=self.instance.pk,
                    fallback=mixin.slug_fallback,
                    max_length=mixin.slug_max_length,
                    scope_filter=scope,
                    slug_field=mixin.slug_field_name,
                )
                return cleaned

        FormWithSlugLock.__name__ = f"{BaseForm.__name__}SlugLock"
        return FormWithSlugLock

    def get_fieldsets(self, request, obj=None):
        fieldsets = list(super().get_fieldsets(request, obj))
        return _inject_slug_unlock(fieldsets, self.slug_field_name)

    def save_model(self, request, obj, form, change):
        creating = obj.pk is None
        super().save_model(request, obj, form, change)
        unlock = bool(form.cleaned_data.get("slug_unlock")) if form else False
        if creating and obj.pk and not unlock:
            source = getattr(obj, self.slug_source_field, "") or ""
            scope = None
            if callable(self.slug_scope_from_instance):
                scope = self.slug_scope_from_instance(obj, {})
            final = unique_slug(
                type(obj),
                source,
                pk=obj.pk,
                fallback=self.slug_fallback,
                max_length=self.slug_max_length,
                scope_filter=scope,
                slug_field=self.slug_field_name,
            )
            if final != getattr(obj, self.slug_field_name):
                type(obj).objects.filter(pk=obj.pk).update(
                    **{self.slug_field_name: final}
                )
                setattr(obj, self.slug_field_name, final)
