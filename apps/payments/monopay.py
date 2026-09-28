"""Monobank Acquiring (Monopay) — invoice create + webhook verify."""
from __future__ import annotations

import base64
import hashlib
import json
import logging
import time
import urllib.error
import urllib.request
from decimal import Decimal, ROUND_HALF_UP

import ecdsa
from django.conf import settings

logger = logging.getLogger(__name__)

API_BASE = "https://api.monobank.ua"
CCY_UAH = 980
_PUBKEY_CACHE: dict[str, object] = {"key": "", "ts": 0.0}
_PUBKEY_TTL_SEC = 3600


class MonopayError(Exception):
    """Raised when Monobank API rejects or fails a request."""


class MonopayService:
    def __init__(self, token: str | None = None):
        self.token = (token if token is not None else settings.MONOPAY_TOKEN) or ""

    @property
    def is_configured(self) -> bool:
        return bool(self.token.strip())

    @staticmethod
    def amount_to_kopiyky(amount: Decimal | float | str) -> int:
        value = Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return int(value * 100)

    def create_invoice(
        self,
        *,
        order_number: str,
        amount: Decimal | float | str,
        description: str,
        redirect_url: str,
        webhook_url: str,
    ) -> dict:
        payload = {
            "amount": self.amount_to_kopiyky(amount),
            "ccy": CCY_UAH,
            "merchantPaymInfo": {
                "reference": order_number,
                "destination": description[:280],
            },
            "redirectUrl": redirect_url,
            "webHookUrl": webhook_url,
        }
        data = self._request("POST", "/api/merchant/invoice/create", payload)
        invoice_id = data.get("invoiceId") or ""
        page_url = data.get("pageUrl") or ""
        if not invoice_id or not page_url:
            raise MonopayError("Monopay response missing invoiceId/pageUrl")
        return {"invoice_id": invoice_id, "page_url": page_url, "raw": data}

    def fetch_pubkey(self) -> str:
        now = time.time()
        cached = str(_PUBKEY_CACHE.get("key") or "")
        ts = float(_PUBKEY_CACHE.get("ts") or 0)
        if cached and (now - ts) < _PUBKEY_TTL_SEC:
            return cached
        data = self._request("GET", "/api/merchant/pubkey")
        key = (data.get("key") or "").strip()
        if not key:
            raise MonopayError("Monopay pubkey empty")
        _PUBKEY_CACHE["key"] = key
        _PUBKEY_CACHE["ts"] = now
        return key

    def verify_webhook(self, body: bytes, x_sign_b64: str, *, pubkey_b64: str | None = None) -> bool:
        if not body or not x_sign_b64:
            return False
        try:
            pub_b64 = pubkey_b64 if pubkey_b64 is not None else self.fetch_pubkey()
            pub_pem = base64.b64decode(pub_b64).decode()
            signature = base64.b64decode(x_sign_b64)
            vk = ecdsa.VerifyingKey.from_pem(pub_pem)
            return bool(
                vk.verify(
                    signature,
                    body,
                    sigdecode=ecdsa.util.sigdecode_der,
                    hashfunc=hashlib.sha256,
                )
            )
        except Exception:
            logger.exception("Monopay webhook signature verify failed")
            return False

    def _request(self, method: str, path: str, payload: dict | None = None) -> dict:
        if not self.is_configured:
            raise MonopayError("MONOPAY_TOKEN is not configured")
        url = f"{API_BASE}{path}"
        headers = {
            "X-Token": self.token.strip(),
            "Accept": "application/json",
        }
        body = None
        if payload is not None:
            body = json.dumps(payload, ensure_ascii=False).encode()
            headers["Content-Type"] = "application/json"
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = resp.read().decode()
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode(errors="replace")[:500]
            logger.error("Monopay HTTP %s %s: %s", method, path, detail)
            raise MonopayError(f"Monopay HTTP {exc.code}: {detail}") from exc
        except urllib.error.URLError as exc:
            logger.error("Monopay network error %s %s: %s", method, path, exc)
            raise MonopayError(f"Monopay network error: {exc}") from exc
