"""Nova Poshta API client — cities / warehouses lookup."""
from __future__ import annotations

import logging
from typing import Any

import json
from urllib import request as urlrequest

from django.conf import settings

logger = logging.getLogger(__name__)

NP_API_URL = "https://api.novaposhta.ua/v2.0/json/"


class NovaPoshtaClient:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or settings.NP_API_KEY

    def call(self, model_name: str, method: str, props: dict | None = None) -> list[dict]:
        if not self.api_key:
            logger.warning("NP_API_KEY is empty — returning empty list")
            return []
        payload = {
            "apiKey": self.api_key,
            "modelName": model_name,
            "calledMethod": method,
            "methodProperties": props or {},
        }
        try:
            data = json.dumps(payload).encode()
            req = urlrequest.Request(
                NP_API_URL,
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urlrequest.urlopen(req, timeout=20) as resp:
                body = json.loads(resp.read().decode())
            if not body.get("success"):
                logger.error("Nova Poshta error: %s", body.get("errors"))
                return []
            return body.get("data") or []
        except Exception:
            logger.exception("Nova Poshta request failed")
            return []

    def search_cities(self, query: str, limit: int = 20) -> list[dict[str, Any]]:
        rows = self.call(
            "Address",
            "searchSettlements",
            {"CityName": query, "Limit": str(limit)},
        )
        # searchSettlements nests addresses
        result = []
        for row in rows:
            for addr in row.get("Addresses") or []:
                result.append(
                    {
                        "ref": addr.get("DeliveryCity") or addr.get("Ref"),
                        "name": addr.get("Present") or addr.get("MainDescription"),
                    }
                )
        if result:
            return result
        # Fallback getCities
        rows = self.call(
            "Address",
            "getCities",
            {"FindByString": query, "Page": "1", "Limit": str(limit)},
        )
        return [{"ref": r.get("Ref"), "name": r.get("Description")} for r in rows]

    def get_warehouses(self, city_ref: str, query: str = "") -> list[dict[str, Any]]:
        props: dict[str, str] = {
            "CityRef": city_ref,
            "Page": "1",
            "Limit": "100",
        }
        if query:
            props["FindByString"] = query
        rows = self.call("Address", "getWarehouses", props)
        return [
            {
                "ref": r.get("Ref"),
                "name": r.get("Description"),
                "point_type": (
                    "locker"
                    if "Поштомат" in (r.get("Description") or "")
                    or str(r.get("CategoryOfWarehouse")) == "Postomat"
                    else "warehouse"
                ),
            }
            for r in rows
        ]
