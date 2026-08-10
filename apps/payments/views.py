import logging

from django.conf import settings
from django.db import IntegrityError, transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST

from apps.orders.models import Order, OrderStatus, PaymentType
from apps.orders.services_status import OrderStatusService

from .liqpay import LiqPayService
from .models import PaymentAttempt

logger = logging.getLogger(__name__)


def start_liqpay_payment(request, order: Order):
    """Create PaymentAttempt and return LiqPay checkout form context or None."""
    service = LiqPayService()
    if not service.is_configured:
        logger.warning("LiqPay is not configured")
        return None

    result_url = request.build_absolute_uri(reverse("payments:liqpay_return"))
    server_url = settings.LIQPAY_SERVER_URL or request.build_absolute_uri(
        reverse("payments:liqpay_callback")
    )
    form_data = service.create_checkout_data(
        order_id=order.order_number,
        amount=float(order.total),
        description=f"Order {order.order_number}",
        result_url=result_url,
        server_url=server_url,
    )
    PaymentAttempt.objects.create(
        order=order,
        provider="liqpay",
        provider_order_id=order.order_number,
        status=PaymentAttempt.Status.CREATED,
        raw_payload={"checkout": True},
    )
    return form_data


@csrf_exempt
@require_http_methods(["POST"])
def liqpay_callback(request):
    data_b64 = request.POST.get("data", "")
    signature = request.POST.get("signature", "")
    if not data_b64 or not signature:
        return HttpResponse("Bad request", status=400)

    service = LiqPayService()
    if not service.verify_callback(data_b64, signature):
        return HttpResponse("Invalid signature", status=403)

    payload = service.decode_data(data_b64)
    order_number = payload.get("order_id", "")
    status = payload.get("status", "")
    payment_id = str(payload.get("payment_id", ""))
    if not order_number:
        return HttpResponse("Missing order_id", status=400)

    idem_key = f"liqpay_{payment_id}_{status}"
    try:
        with transaction.atomic():
            order = Order.objects.select_for_update().get(order_number=order_number)
            if PaymentAttempt.objects.filter(idempotency_key=idem_key).exists():
                return HttpResponse("OK (idempotent)", status=200)

            try:
                attempt = PaymentAttempt.objects.create(
                    order=order,
                    provider="liqpay",
                    provider_order_id=order_number,
                    payment_id=payment_id,
                    idempotency_key=idem_key,
                    raw_payload=payload,
                    status=PaymentAttempt.Status.CREATED,
                )
            except IntegrityError:
                # Паралельний callback з тим самим payment_id+status.
                return HttpResponse("OK (idempotent)", status=200)

            if status in ("success", "sandbox"):
                attempt.status = (
                    PaymentAttempt.Status.SANDBOX
                    if status == "sandbox"
                    else PaymentAttempt.Status.SUCCESS
                )
                attempt.save(update_fields=["status"])
                if order.status == OrderStatus.AWAITING_PAYMENT:
                    # Один лист клієнту після фінального статусу «В обробці».
                    OrderStatusService.transition(order, OrderStatus.PAID, notify=False)
                    OrderStatusService.transition(order, OrderStatus.PROCESSING, notify=True)
            elif status in ("failure", "error", "reversed"):
                attempt.status = PaymentAttempt.Status.FAILURE
                attempt.save(update_fields=["status"])
        return HttpResponse("OK", status=200)
    except Order.DoesNotExist:
        return HttpResponse("Order not found", status=404)
    except Exception:
        logger.exception("LiqPay callback error")
        return HttpResponse("Internal error", status=500)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def liqpay_return(request):
    data_b64 = request.POST.get("data", "")
    signature = request.POST.get("signature", "")
    order = None
    service = LiqPayService()

    if data_b64 and signature and service.verify_callback(data_b64, signature):
        payload = service.decode_data(data_b64)
        order = Order.objects.filter(order_number=payload.get("order_id")).first()
    else:
        token = request.session.get("last_order_token")
        if token:
            order = Order.objects.filter(access_token=token).first()

    if not order:
        return redirect("orders:thank_you")

    url = (
        reverse("orders:thank_you")
        + f"?order={order.order_number}&t={order.access_token}"
    )
    return redirect(url)


@require_POST
def liqpay_retry(request):
    token = request.POST.get("t") or request.session.get("last_order_token")
    order = get_object_or_404(Order, access_token=token)
    if order.payment_type != PaymentType.LIQPAY:
        return redirect("orders:thank_you")
    if order.status not in (OrderStatus.AWAITING_PAYMENT, OrderStatus.NEW):
        url = (
            reverse("orders:thank_you")
            + f"?order={order.order_number}&t={order.access_token}"
        )
        return redirect(url)
    form_data = start_liqpay_payment(request, order)
    if not form_data:
        return redirect(
            reverse("orders:thank_you")
            + f"?order={order.order_number}&t={order.access_token}"
        )
    return render(
        request,
        "payments/liqpay_redirect.html",
        {"order": order, "liqpay": form_data},
    )
