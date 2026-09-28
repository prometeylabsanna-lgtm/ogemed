import json
import logging
from urllib.parse import urlencode

from django.conf import settings
from django.db import IntegrityError, transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST

from apps.orders.models import Order, OrderStatus, PaymentType
from apps.orders.services_status import OrderStatusService

from .models import PaymentAttempt
from .monopay import MonopayError, MonopayService

logger = logging.getLogger(__name__)


def _thank_you_url(order: Order) -> str:
    return (
        reverse("orders:thank_you")
        + "?"
        + urlencode({"order": order.order_number, "t": order.access_token})
    )


def start_monopay_payment(request, order: Order) -> dict | None:
    """Create invoice; return {page_url, invoice_id} or None if not configured / API fail."""
    service = MonopayService()
    if not service.is_configured:
        logger.warning("Monopay is not configured")
        return None

    redirect_url = request.build_absolute_uri(_thank_you_url(order))
    webhook_url = settings.MONOPAY_WEBHOOK_URL or request.build_absolute_uri(
        reverse("payments:monopay_callback")
    )
    try:
        invoice = service.create_invoice(
            order_number=order.order_number,
            amount=order.total,
            description=f"Замовлення {order.order_number}",
            redirect_url=redirect_url,
            webhook_url=webhook_url,
        )
    except MonopayError:
        logger.exception("Monopay create invoice failed for %s", order.order_number)
        return None

    PaymentAttempt.objects.create(
        order=order,
        provider="monopay",
        provider_order_id=invoice["invoice_id"],
        payment_id=invoice["invoice_id"],
        status=PaymentAttempt.Status.CREATED,
        raw_payload=invoice.get("raw") or {},
    )
    return invoice


@csrf_exempt
@require_http_methods(["POST"])
def monopay_callback(request):
    body = request.body or b""
    x_sign = request.headers.get("X-Sign", "")
    service = MonopayService()
    if not service.is_configured:
        return HttpResponse("Not configured", status=503)
    if not service.verify_webhook(body, x_sign):
        return HttpResponse("Invalid signature", status=403)

    try:
        payload = json.loads(body.decode())
    except (UnicodeDecodeError, json.JSONDecodeError):
        return HttpResponse("Bad JSON", status=400)

    status = (payload.get("status") or "").strip()
    invoice_id = str(payload.get("invoiceId") or "")
    order_number = str(payload.get("reference") or "")
    modified = str(payload.get("modifiedDate") or "")
    if not order_number or not invoice_id:
        return HttpResponse("Missing reference/invoiceId", status=400)

    idem_key = f"monopay_{invoice_id}_{status}_{modified}"
    try:
        with transaction.atomic():
            order = Order.objects.select_for_update().get(order_number=order_number)
            if PaymentAttempt.objects.filter(idempotency_key=idem_key).exists():
                return HttpResponse("OK (idempotent)", status=200)

            try:
                attempt = PaymentAttempt.objects.create(
                    order=order,
                    provider="monopay",
                    provider_order_id=invoice_id,
                    payment_id=invoice_id,
                    idempotency_key=idem_key,
                    raw_payload=payload,
                    status=PaymentAttempt.Status.CREATED,
                )
            except IntegrityError:
                return HttpResponse("OK (idempotent)", status=200)

            if status == "success":
                attempt.status = PaymentAttempt.Status.SUCCESS
                attempt.save(update_fields=["status"])
                if order.status == OrderStatus.AWAITING_PAYMENT:
                    OrderStatusService.transition(order, OrderStatus.PAID, notify=False)
                    OrderStatusService.transition(
                        order, OrderStatus.PROCESSING, notify=True
                    )
            elif status in ("failure", "expired", "reversed"):
                attempt.status = PaymentAttempt.Status.FAILURE
                attempt.save(update_fields=["status"])
        return HttpResponse("OK", status=200)
    except Order.DoesNotExist:
        return HttpResponse("Order not found", status=404)
    except Exception:
        logger.exception("Monopay callback error")
        return HttpResponse("Internal error", status=500)


@require_POST
def monopay_retry(request):
    token = request.POST.get("t") or request.session.get("last_order_token")
    order = get_object_or_404(Order, access_token=token)
    if order.payment_type != PaymentType.MONOPAY:
        return redirect("orders:thank_you")
    if order.status not in (OrderStatus.AWAITING_PAYMENT, OrderStatus.NEW):
        return redirect(_thank_you_url(order))
    invoice = start_monopay_payment(request, order)
    if not invoice:
        return redirect(_thank_you_url(order))
    return HttpResponseRedirect(invoice["page_url"])
