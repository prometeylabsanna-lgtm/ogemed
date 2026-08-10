from django.http import HttpResponse
from django.shortcuts import render
from django.utils.translation import gettext as _
from django.views.generic import TemplateView

from apps.catalog.models import Brand
from apps.catalog.services import hits_products, home_quick_categories, new_products
from apps.cms.models import HeroSlide


def health(request) -> HttpResponse:
    """Lightweight health endpoint for monitoring (no DB)."""
    return HttpResponse("ok", content_type="text/plain")


def page_not_found(request, exception):
    return render(request, "404.html", status=404)


class HomeView(TemplateView):
    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = _("OGEMED for you")
        ctx["meta_description"] = _(
            "Інтернет-магазин косметики OGEMED for you"
        )
        ctx["breadcrumbs"] = None
        ctx["hero_slides"] = HeroSlide.objects.filter(is_active=True)
        ctx["hits"] = hits_products(8)
        ctx["new_items"] = new_products(8)
        ctx["quick_categories"] = home_quick_categories(8)
        ctx["featured_brands"] = Brand.objects.filter(
            is_active=True, is_featured=True
        ).order_by("sort_order", "name_uk")[:3]
        return ctx
