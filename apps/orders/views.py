from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views import View
from django.views.generic import TemplateView

from apps.cart.cart import SessionCart
from apps.core.breadcrumbs import build_breadcrumbs
from apps.notify.services import notify_new_order
from apps.orders.models import Order, OrderStatus, PaymentType
from apps.payments.views import start_liqpay_payment

from .forms import CheckoutForm
from .services_checkout import InsufficientStockError, create_order_from_cart


class CheckoutView(View):
    template_name = "orders/checkout.html"

    def get(self, request):
        cart = SessionCart(request)
        if cart.is_empty():
            messages.info(request, _("Кошик порожній"))
            return redirect("cart:detail")
        initial = {}
        if request.user.is_authenticated:
            initial["customer_email"] = request.user.email
            profile = getattr(request.user, "profile", None)
            if profile:
                initial["customer_name"] = profile.full_name
                initial["customer_phone"] = profile.phone
                # Адреса за замовчуванням → курʼєрські поля checkout.
                if profile.default_city:
                    initial["courier_city"] = profile.default_city
                if profile.default_street:
                    initial["courier_street"] = profile.default_street
                if profile.default_building:
                    initial["courier_building"] = profile.default_building
                if profile.default_apartment:
                    initial["courier_apartment"] = profile.default_apartment
                if any(
                    [
                        profile.default_city,
                        profile.default_street,
                        profile.default_building,
                    ]
                ):
                    from apps.orders.models import DeliveryType

                    initial.setdefault("delivery_type", DeliveryType.COURIER)
        form = CheckoutForm(initial=initial)
        return render(request, self.template_name, self._context(request, form, cart))

    def post(self, request):
        cart = SessionCart(request)
        if cart.is_empty():
            return redirect("cart:detail")
        form = CheckoutForm(request.POST)
        if not form.is_valid():
            return render(
                request, self.template_name, self._context(request, form, cart), status=400
            )
        try:
            order = create_order_from_cart(request, form.cleaned_data)
        except InsufficientStockError as exc:
            messages.error(request, str(exc))
            return render(
                request, self.template_name, self._context(request, form, cart), status=400
            )
        notify_new_order(order)
        if order.payment_type == PaymentType.LIQPAY:
            form_data = start_liqpay_payment(request, order)
            if form_data:
                return render(
                    request,
                    "payments/liqpay_redirect.html",
                    {"order": order, "liqpay": form_data},
                )
        url = reverse("orders:thank_you") + f"?order={order.order_number}&t={order.access_token}"
        return redirect(url)

    def _context(self, request, form, cart):
        return {
            "form": form,
            "cart": cart,
            "lines": cart.lines(),
            "cart_total": cart.total,
            "page_title": _("Оформлення"),
            "robots_noindex": True,
            "breadcrumbs": build_breadcrumbs(
                request,
                (_("Кошик"), reverse("cart:detail")),
                (_("Оформлення"), None),
            ),
        }


class ThankYouView(TemplateView):
    template_name = "orders/thank_you.html"

    def get(self, request, *args, **kwargs):
        order = self._resolve_order(request)
        context = self.get_context_data(order=order)
        if order is None:
            return render(request, self.template_name, context, status=404)
        return render(request, self.template_name, context)

    def _resolve_order(self, request) -> Order | None:
        order_number = request.GET.get("order") or ""
        token = request.GET.get("t") or ""
        session_token = request.session.get("last_order_token") or ""

        if not order_number and not token and not session_token:
            return None

        qs = Order.objects.prefetch_related("items")
        order = None
        if token:
            order = qs.filter(access_token=token).first()
        elif order_number and session_token:
            order = qs.filter(order_number=order_number, access_token=session_token).first()
        elif order_number and request.user.is_authenticated:
            order = qs.filter(order_number=order_number, user=request.user).first()
        elif session_token:
            order = qs.filter(access_token=session_token).first()

        if order is None:
            return None

        # Soft IDOR guard: token or owner or matching session token.
        if token and order.access_token == token:
            return order
        if session_token and order.access_token == session_token:
            return order
        if request.user.is_authenticated and order.user_id == request.user.id:
            return order
        return None

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        order = kwargs.get("order")
        ctx["order"] = order
        ctx["page_title"] = _("Дякуємо")
        ctx["robots_noindex"] = True
        crumbs = [(_("Оформлення"), reverse("orders:checkout")), (_("Дякуємо"), None)]
        ctx["breadcrumbs"] = build_breadcrumbs(self.request, *crumbs)
        ctx["show_retry"] = bool(
            order and order.status == OrderStatus.AWAITING_PAYMENT
            and order.payment_type == PaymentType.LIQPAY
        )
        return ctx
