from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView

from apps.core.breadcrumbs import build_breadcrumbs

from .cart import SessionCart


class CartDetailView(TemplateView):
    template_name = "cart/detail.html"

    def get_template_names(self):
        if self.request.htmx:
            return ["cart/partials/_cart_panel.html"]
        return [self.template_name]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        cart = SessionCart(self.request)
        ctx["cart"] = cart
        ctx["lines"] = cart.lines()
        ctx["cart_total"] = cart.total
        ctx["page_title"] = _("Кошик")
        ctx["robots_noindex"] = True
        ctx["breadcrumbs"] = build_breadcrumbs(self.request, (_("Кошик"), None))
        return ctx


def _cart_response(request, *, status: int = 200, open_popup: bool = False):
    cart = SessionCart(request)
    context = {
        "cart": cart,
        "lines": cart.lines(),
        "cart_total": cart.total,
        "cart_count": len(cart),
    }
    if request.htmx:
        response = render(request, "cart/partials/_cart_panel.html", context, status=status)
        response["HX-Trigger"] = (
            '{"cartUpdated":true'
            + (',"openCartPopup":true' if open_popup else "")
            + "}"
        )
        return response
    return redirect("cart:detail")


@require_POST
def cart_add(request):
    variant_id = request.POST.get("variant_id")
    qty = request.POST.get("quantity", "1")
    if not variant_id:
        return HttpResponseBadRequest("variant_id required")
    cart = SessionCart(request)
    try:
        cart.add(variant_id, int(qty))
    except ValueError:
        return HttpResponseBadRequest("not purchasable")
    return _cart_response(request, open_popup=True)


@require_POST
def cart_update(request):
    variant_id = request.POST.get("variant_id")
    qty = request.POST.get("quantity", "1")
    if not variant_id:
        return HttpResponseBadRequest("variant_id required")
    try:
        SessionCart(request).set_qty(variant_id, int(qty))
    except ValueError:
        return HttpResponseBadRequest("invalid quantity")
    return _cart_response(request)


@require_POST
def cart_remove(request):
    variant_id = request.POST.get("variant_id")
    if not variant_id:
        return HttpResponseBadRequest("variant_id required")
    SessionCart(request).remove(variant_id)
    if request.htmx:
        return _cart_response(request)
    nxt = request.POST.get("next", "")
    if nxt.startswith("/") and not nxt.startswith("//"):
        return redirect(nxt)
    return redirect("cart:detail")


def cart_count_partial(request):
    cart = SessionCart(request)
    return HttpResponse(str(len(cart)))
