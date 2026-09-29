"""Proxy-адмінки юридичних сторінок → єдиний редактор."""
from __future__ import annotations

from django.contrib import admin
from unfold.admin import ModelAdmin

from apps.cms.admin_legal_pages import legal_page_edit_view
from apps.cms.legal_page_registry import LEGAL_PAGES, LEGAL_PAGES_BY_MODEL
from apps.cms.models import (
    LegalAboutPage,
    LegalContactsPage,
    LegalOfferPage,
    LegalPrivacyPage,
    LegalReturnsPage,
    LegalShippingPage,
)

_PROXY_MODELS = (
    LegalAboutPage,
    LegalContactsPage,
    LegalShippingPage,
    LegalReturnsPage,
    LegalPrivacyPage,
    LegalOfferPage,
)


class LegalPageAdmin(ModelAdmin):
    """Changelist відкриває повний редактор сторінки (без списків секцій)."""

    page_key: str = ""

    def has_add_permission(self, request) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return False

    def changelist_view(self, request, extra_context=None):
        page_key = self.page_key
        if not page_key:
            defn = LEGAL_PAGES_BY_MODEL.get(self.model._meta.model_name)
            if defn is None:
                from django.http import Http404

                raise Http404
            page_key = defn.key
        return legal_page_edit_view(request, page_key, model_admin=self)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        return self.changelist_view(request, extra_context)


def register_legal_page_admins() -> None:
    by_name = {m.__name__: m for m in _PROXY_MODELS}
    for defn in LEGAL_PAGES:
        model = by_name.get(
            {
                "legalaboutpage": "LegalAboutPage",
                "legalcontactspage": "LegalContactsPage",
                "legalshippingpage": "LegalShippingPage",
                "legalreturnspage": "LegalReturnsPage",
                "legalprivacypage": "LegalPrivacyPage",
                "legalofferpage": "LegalOfferPage",
            }[defn.model_name]
        )
        if model is None or model in admin.site._registry:
            continue

        class PageAdmin(LegalPageAdmin):
            pass

        PageAdmin.__name__ = f"{model.__name__}Admin"
        PageAdmin.page_key = defn.key
        admin.site.register(model, PageAdmin)


register_legal_page_admins()
