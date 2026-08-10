"""Integration env helpers — secrets stay in env; missing keys degrade gracefully."""
from __future__ import annotations

from dataclasses import dataclass

from django.conf import settings


@dataclass(frozen=True)
class IntegrationStatus:
    key: str
    configured: bool
    detail: str = ""


def _present(*values: str) -> bool:
    return all(bool((v or "").strip()) for v in values)


def resend_status() -> IntegrationStatus:
    key = (settings.RESEND_API_KEY or "").strip()
    from_email = (settings.FROM_EMAIL or "").strip()
    ok = bool(key)
    detail = "ok" if ok else "RESEND_API_KEY empty — emails skipped"
    if ok and not from_email:
        detail = "FROM_EMAIL empty — fallback noreply@example.com"
    return IntegrationStatus("resend", ok, detail)


def liqpay_status() -> IntegrationStatus:
    ok = _present(settings.LIQPAY_PUBLIC_KEY, settings.LIQPAY_PRIVATE_KEY)
    detail = "ok" if ok else "LIQPAY_* keys missing — online pay disabled"
    return IntegrationStatus("liqpay", ok, detail)


def nova_poshta_status() -> IntegrationStatus:
    ok = bool((settings.NP_API_KEY or "").strip())
    detail = "ok" if ok else "NP_API_KEY empty — city/warehouse lists empty"
    return IntegrationStatus("nova_poshta", ok, detail)


def telegram_status() -> IntegrationStatus:
    ok = _present(settings.TELEGRAM_BOT_TOKEN, settings.TELEGRAM_ADMIN_CHAT_ID)
    detail = "ok" if ok else "TELEGRAM_* missing — admin Telegram skipped"
    return IntegrationStatus("telegram", ok, detail)


def viber_status() -> IntegrationStatus:
    ok = _present(settings.VIBER_AUTH_TOKEN, settings.VIBER_ADMIN_ID)
    detail = "ok" if ok else "VIBER_* missing — admin Viber skipped"
    return IntegrationStatus("viber", ok, detail)


def all_integration_statuses() -> list[IntegrationStatus]:
    return [
        resend_status(),
        liqpay_status(),
        nova_poshta_status(),
        telegram_status(),
        viber_status(),
    ]
