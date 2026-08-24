"""Notify adapters — best-effort email / Telegram / Viber (queue-ready)."""
from __future__ import annotations

import json
import logging
from typing import Protocol
from urllib import request as urlrequest
from urllib.parse import urlencode

from django.conf import settings
from django.db import transaction
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


class Notifier(Protocol):
    def send(self, subject: str, body: str, **kwargs) -> None: ...


def _manager_email() -> str:
    try:
        from apps.core.models import SiteSettings

        email = (SiteSettings.load().manager_email or "").strip()
        if email:
            return email
    except Exception:
        logger.debug("SiteSettings manager_email unavailable", exc_info=True)
    return (settings.FROM_EMAIL or "").strip()


def _render_email(template_stem: str, context: dict) -> tuple[str, str]:
    html_body = render_to_string(f"notify/email/{template_stem}.html", context)
    text_body = render_to_string(f"notify/email/{template_stem}.txt", context)
    return html_body, text_body.strip()


def _enqueue_or_run(func_path: str, *args) -> None:
    """After commit: sync call або Django-Q2 async_task."""

    def _run():
        try:
            if getattr(settings, "NOTIFY_USE_QUEUE", False):
                from django_q.tasks import async_task

                async_task(func_path, *args)
            else:
                from django.utils.module_loading import import_string

                import_string(func_path)(*args)
        except Exception:
            logger.exception("Notify dispatch failed: %s", func_path)

    transaction.on_commit(_run)


def send_email(to: str, subject: str, html_body: str, text_body: str = "") -> None:
    """Email via Resend API. No-op when API key or recipient missing."""
    if not to:
        return
    api_key = (settings.RESEND_API_KEY or "").strip()
    from_email = (settings.FROM_EMAIL or "").strip() or "noreply@example.com"
    if not api_key:
        logger.info("RESEND_API_KEY missing — email skipped to=%s subject=%s", to, subject)
        return
    payload = {
        "from": from_email,
        "to": [to],
        "subject": subject,
        "html": html_body,
    }
    if text_body:
        payload["text"] = text_body
    req = urlrequest.Request(
        "https://api.resend.com/emails",
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urlrequest.urlopen(req, timeout=20) as resp:
        resp.read()


def send_telegram(text: str) -> None:
    token = (settings.TELEGRAM_BOT_TOKEN or "").strip()
    chat_id = (settings.TELEGRAM_ADMIN_CHAT_ID or "").strip()
    if not token or not chat_id:
        logger.info("Telegram not configured — skipped")
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urlencode(
        {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    ).encode()
    req = urlrequest.Request(url, data=data, method="POST")
    with urlrequest.urlopen(req, timeout=15) as resp:
        resp.read()


def send_viber(text: str) -> None:
    token = (settings.VIBER_AUTH_TOKEN or "").strip()
    admin_id = (settings.VIBER_ADMIN_ID or "").strip()
    if not token or not admin_id:
        logger.info("Viber not configured — skipped")
        return
    payload = {
        "receiver": admin_id,
        "type": "text",
        "text": text[:1000],
        "sender": {"name": "OGEMED"},
    }
    req = urlrequest.Request(
        "https://chatapi.viber.com/pa/send_message",
        data=json.dumps(payload).encode(),
        headers={
            "X-Viber-Auth-Token": token,
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urlrequest.urlopen(req, timeout=15) as resp:
        resp.read()


def task_notify_new_order(order_id: int) -> None:
    from apps.orders.fop_payment import fop_payment_details
    from apps.orders.models import Order, PaymentType

    order = Order.objects.filter(pk=order_id).first()
    if not order:
        return

    fop = fop_payment_details(order) if order.payment_type == PaymentType.FOP_CARD else None
    manager = _manager_email()
    admin_html, admin_text = _render_email(
        "new_order", {"order": order, "for_customer": False, "fop": fop}
    )
    customer_html, customer_text = _render_email(
        "new_order", {"order": order, "for_customer": True, "fop": fop}
    )
    subject_admin = f"Нове замовлення {order.order_number}"
    subject_customer = f"Ваше замовлення {order.order_number}"
    messenger_text = (
        f"Замовлення {order.order_number}\n"
        f"{order.customer_name}, {order.customer_phone}\n"
        f"Сума: {order.total} грн\n"
        f"Оплата: {order.get_payment_type_display()}\n"
        f"Статус: {order.get_status_display()}"
    )
    if manager:
        send_email(manager, subject_admin, admin_html, admin_text)
    if order.customer_email:
        send_email(
            order.customer_email,
            subject_customer,
            customer_html,
            customer_text,
        )
    send_telegram(messenger_text)
    send_viber(messenger_text)


def task_notify_order_status(order_id: int, previous_status: str) -> None:
    from apps.orders.models import Order, OrderStatus

    order = Order.objects.filter(pk=order_id).first()
    if not order or not order.customer_email:
        return
    if previous_status == order.status:
        return
    previous_label = dict(OrderStatus.choices).get(previous_status, previous_status)
    html_body, text_body = _render_email(
        "order_status",
        {
            "order": order,
            "previous_status": previous_status,
            "previous_status_label": previous_label,
        },
    )
    subject = f"Статус замовлення {order.order_number}: {order.get_status_display()}"
    send_email(order.customer_email, subject, html_body, text_body)


def task_notify_new_lead(lead_id: int) -> None:
    from apps.cms.models import Lead

    lead = Lead.objects.filter(pk=lead_id).first()
    if not lead:
        return
    html_body, text_body = _render_email("new_lead", {"lead": lead})
    subject = f"Заявка: {lead.get_lead_type_display()}"
    messenger_text = (
        f"Заявка {lead.get_lead_type_display()}: "
        f"{lead.name}, {lead.phone}, {lead.email or '—'}"
    )
    if lead.message:
        messenger_text = f"{messenger_text}\n{lead.message}"
    manager = _manager_email()
    if manager:
        send_email(manager, subject, html_body, text_body)
    send_telegram(messenger_text)
    send_viber(messenger_text)


def notify_new_order(order) -> None:
    _enqueue_or_run("apps.notify.services.task_notify_new_order", order.pk)


def notify_order_status_changed(order, *, previous_status: str) -> None:
    if not order.customer_email or previous_status == order.status:
        return
    _enqueue_or_run(
        "apps.notify.services.task_notify_order_status",
        order.pk,
        previous_status,
    )


def notify_new_lead(lead) -> None:
    _enqueue_or_run("apps.notify.services.task_notify_new_lead", lead.pk)
