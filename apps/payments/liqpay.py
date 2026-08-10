"""LiqPay Acquiring v3 service."""
from __future__ import annotations

import base64
import hashlib
import json
import logging

from django.conf import settings

logger = logging.getLogger(__name__)

LIQPAY_CHECKOUT_URL = "https://www.liqpay.ua/api/3/checkout"


class LiqPayService:
    def __init__(self, public_key: str | None = None, private_key: str | None = None):
        self.public_key = public_key or settings.LIQPAY_PUBLIC_KEY
        self.private_key = private_key or settings.LIQPAY_PRIVATE_KEY

    def _encode(self, payload: dict) -> str:
        return base64.b64encode(
            json.dumps(payload, ensure_ascii=False).encode()
        ).decode()

    def _sign(self, data_b64: str) -> str:
        raw = (self.private_key + data_b64 + self.private_key).encode()
        return base64.b64encode(hashlib.sha1(raw).digest()).decode()

    def decode_data(self, data_b64: str) -> dict:
        try:
            return json.loads(base64.b64decode(data_b64).decode())
        except Exception:
            logger.exception("LiqPay decode failed")
            return {}

    def verify_callback(self, data_b64: str, signature: str) -> bool:
        return self._sign(data_b64) == signature

    def create_checkout_data(
        self,
        *,
        order_id: str,
        amount: float,
        description: str,
        result_url: str,
        server_url: str,
        currency: str = "UAH",
    ) -> dict:
        payload = {
            "public_key": self.public_key,
            "version": "3",
            "action": "pay",
            "amount": amount,
            "currency": currency,
            "description": description,
            "order_id": order_id,
            "result_url": result_url,
            "server_url": server_url,
            "sandbox": 1 if settings.LIQPAY_SANDBOX else 0,
        }
        data_b64 = self._encode(payload)
        return {
            "data": data_b64,
            "signature": self._sign(data_b64),
            "checkout_url": LIQPAY_CHECKOUT_URL,
        }

    @property
    def is_configured(self) -> bool:
        return bool(self.public_key and self.private_key)
