from django.views.generic import DetailView

from apps.core.breadcrumbs import build_breadcrumbs

from .about_content import AboutContent
from .info_page_service import meta_for_page, sections_for_page
from .models import CMSPage


_INFO_TEMPLATES = {
    "about": "cms/about.html",
    "contacts": "cms/contacts.html",
    "shipping": "cms/shipping.html",
    "returns": "cms/returns.html",
    "privacy": "cms/privacy.html",
    "offer": "cms/offer.html",
}

_SLUG_TEMPLATES = {
    "pro-nas": "cms/about.html",
    "kontakty": "cms/contacts.html",
    "dostavka-i-oplata": "cms/shipping.html",
    "povernennya": "cms/returns.html",
    "polityka-konfidentsiynosti": "cms/privacy.html",
    "publichna-oferta": "cms/offer.html",
}

_PAGE_KEY_BY_SLUG = {
    "dostavka-i-oplata": "shipping",
    "povernennya": "returns",
    "polityka-konfidentsiynosti": "privacy",
    "publichna-oferta": "offer",
}


class CMSPageDetailView(DetailView):
    model = CMSPage
    template_name = "cms/page.html"
    context_object_name = "page"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return CMSPage.objects.filter(is_published=True)

    def get_template_names(self):
        page = self.object
        if page.page_key in _INFO_TEMPLATES:
            return [_INFO_TEMPLATES[page.page_key]]
        if page.slug in _SLUG_TEMPLATES:
            return [_SLUG_TEMPLATES[page.slug]]
        return super().get_template_names()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        page = self.object
        ctx["page_title"] = page.title
        body = (page.body or "").strip()
        if body:
            plain = " ".join(body.split())
            ctx["meta_description"] = plain[:160]
        else:
            ctx["meta_description"] = page.title
        ctx["breadcrumbs"] = build_breadcrumbs(
            self.request,
            (page.title, None),
        )
        if page.page_key == "about" or page.slug == "pro-nas":
            ctx["about"] = AboutContent.load()
        self._add_info_page_context(ctx, page)
        return ctx

    def _add_info_page_context(self, ctx: dict, page: CMSPage) -> None:
        key = page.page_key or _PAGE_KEY_BY_SLUG.get(page.slug, "")
        if key not in {"shipping", "returns", "privacy", "offer"}:
            return
        ctx["info_sections"] = sections_for_page(key)
        meta = meta_for_page(key)
        ctx["cta_title"] = meta["cta_title"]
        ctx["cta_text"] = meta["cta_text"]
        ctx["info_note"] = meta["info_note"]
