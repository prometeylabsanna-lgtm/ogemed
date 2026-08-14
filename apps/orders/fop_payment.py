"""Реквізити ФОП для checkout / thank-you / листів (з SiteSettings)."""
from __future__ import annotations

from apps.core.models import SiteSettings
from apps.orders.models import Order, PaymentType


def fop_payment_details(order: Order | None = None) -> dict:
    site = SiteSettings.load()
    purpose = ""
    if order is not None:
        purpose = f"Оплата замовлення №{order.order_number}"
    recipient = (site.fop_recipient_name or "").strip()
    iban = (site.fop_iban or "").strip()
    card = (site.fop_card_number or "").strip()
    edrpou = (site.fop_edrpou or "").strip()
    configured = bool(recipient and (iban or card))
    lines = []
    if recipient:
        lines.append(f"Одержувач: {recipient}")
    if iban:
        lines.append(f"IBAN: {iban}")
    if card:
        lines.append(f"Картка: {card}")
    if edrpou:
        lines.append(f"ЄДРПОУ / ІПН: {edrpou}")
    if purpose:
        lines.append(f"Призначення платежу: {purpose}")
    if order is not None:
        lines.append(f"Сума: {order.total} ₴")
    return {
        "recipient": recipient,
        "iban": iban,
        "card": card,
        "edrpou": edrpou,
        "purpose": purpose,
        "amount": order.total if order is not None else None,
        "configured": configured,
        "copy_text": "\n".join(lines),
        "is_fop": bool(order and order.payment_type == PaymentType.FOP_CARD),
    }
