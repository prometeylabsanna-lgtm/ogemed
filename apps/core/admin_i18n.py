"""Спільний UA/RU перемикач полів у Django admin (Unfold)."""
from __future__ import annotations

LANG_SWITCH_HTML = (
    '<div class="product-admin-editor__langbar product-admin-editor__langbar--inline" '
    'data-cms-lang-switch role="group" aria-label="Мова контенту">'
    '<button type="button" class="cms-lang-switch__btn is-active" data-cms-lang="uk">UA</button>'
    '<button type="button" class="cms-lang-switch__btn" data-cms-lang="ru">RU</button>'
    '<p class="product-admin-editor__langhint">'
    "Перемикач показує текстові поля українською або російською."
    "</p></div>"
)

_LABEL_SUFFIXES = (
    " (UK)",
    " (UA)",
    " (RU)",
    " (uk)",
    " (ru)",
    " UK",
    " UA",
    " RU",
)


class I18nLangTabsMixin:
    """Обгортка форми + Media для перемикача UA/RU по полях *_uk / *_ru."""

    change_form_template = "admin/catalog/i18n_change_form.html"

    class Media:
        css = {"all": ("css/admin/site_content.css", "css/admin/ogemed_theme.css")}
        js = ("js/admin/catalog_lang_tabs.js",)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        for name, field in form.base_fields.items():
            if not (name.endswith("_uk") or name.endswith("_ru")):
                continue
            label = str(field.label or "")
            for suffix in _LABEL_SUFFIXES:
                if label.endswith(suffix):
                    field.label = label[: -len(suffix)].rstrip(" :")
                    break
        return form
