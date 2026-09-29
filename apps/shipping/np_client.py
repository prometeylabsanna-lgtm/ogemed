"""Nova Poshta API client — cities / warehouses lookup."""
from __future__ import annotations

import json
import logging
import time
from typing import Any
from urllib import request as urlrequest

from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

NP_API_URL = "https://api.novaposhta.ua/v2.0/json/"
WAREHOUSE_CACHE_TTL = 60 * 60 * 24  # 24 год — повний довідник по місту
PAGE_SIZE = 500  # ліміт NP на сторінку
MAX_PAGES = 40  # safety: до 20k точок на тип
REQUEST_RETRIES = 3


class NovaPoshtaClient:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or settings.NP_API_KEY

    def call(self, model_name: str, method: str, props: dict | None = None) -> list[dict]:
        data, ok = self._request(model_name, method, props)
        return data if ok else []

    def _request(
        self, model_name: str, method: str, props: dict | None = None
    ) -> tuple[list[dict], bool]:
        """Повертає (data, ok). ok=False — мережа/API-помилка; ok=True і [] — кінець сторінок."""
        if not self.api_key:
            logger.warning("NP_API_KEY is empty — returning empty list")
            return [], False
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
            with urlrequest.urlopen(req, timeout=45) as resp:
                body = json.loads(resp.read().decode())
            if not body.get("success"):
                logger.error("Nova Poshta error: %s", body.get("errors"))
                return [], False
            return body.get("data") or [], True
        except Exception:
            logger.exception("Nova Poshta request failed")
            return [], False

    def _request_retry(
        self, model_name: str, method: str, props: dict | None = None
    ) -> tuple[list[dict], bool]:
        last: tuple[list[dict], bool] = ([], False)
        for attempt in range(REQUEST_RETRIES):
            last = self._request(model_name, method, props)
            if last[1]:
                return last
            if attempt + 1 < REQUEST_RETRIES:
                time.sleep(0.35 * (attempt + 1))
        return last

    def search_cities(self, query: str, limit: int = 20) -> list[dict[str, Any]]:
        rows = self.call(
            "Address",
            "searchSettlements",
            {"CityName": query, "Limit": str(limit)},
        )
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
        rows = self.call(
            "Address",
            "getCities",
            {"FindByString": query, "Page": "1", "Limit": str(limit)},
        )
        return [{"ref": r.get("Ref"), "name": r.get("Description")} for r in rows]

    def search_warehouses(self, city_ref: str, query: str) -> list[dict[str, Any]]:
        """Повний довідник міста з кешу + локальний фільтр (відділення, пункти, поштомати)."""
        q = (query or "").strip().casefold()
        if not city_ref or len(q) < 2:
            return []
        items = self.list_city_warehouses(city_ref)
        return [row for row in items if q in (row.get("name") or "").casefold()]

    def list_city_warehouses(self, city_ref: str) -> list[dict[str, Any]]:
        city_ref = (city_ref or "").strip()
        if not city_ref:
            return []
        cache_key = f"np:warehouses:v2:{city_ref}"
        cached = cache.get(cache_key)
        if isinstance(cached, list):
            return cached

        rows = self._fetch_all_warehouses(city_ref)
        if rows is None:
            return []
        mapped = self._dedupe_mapped(rows)
        cache.set(cache_key, mapped, WAREHOUSE_CACHE_TTL)
        return mapped

    def get_warehouses(self, city_ref: str, query: str = "") -> list[dict[str, Any]]:
        """Сумісність: пошук по місту (повний довідник + фільтр)."""
        if query:
            return self.search_warehouses(city_ref, query)
        return self.list_city_warehouses(city_ref)

    def _warehouse_type_refs(self) -> list[str | None]:
        """Окремі запити по типах — рекомендація NP (ліміт ~6500 на відповідь)."""
        types, ok = self._request_retry("Address", "getWarehouseTypes", {})
        refs: list[str] = []
        if ok:
            for row in types:
                ref = (row.get("Ref") or "").strip()
                if ref and ref not in refs:
                    refs.append(ref)
        if refs:
            return refs  # type: ignore[return-value]
        return [None]

    def _fetch_all_warehouses(self, city_ref: str) -> list[dict] | None:
        """Усі сирі рядки getWarehouses для міста. None — збій (не кешуємо)."""
        collected: list[dict] = []
        seen: set[str] = set()
        type_refs = self._warehouse_type_refs()
        for type_ref in type_refs:
            page_rows = self._paginate_city(city_ref, type_ref)
            if page_rows is None:
                return None
            for row in page_rows:
                ref = row.get("Ref") or ""
                if not ref or ref in seen:
                    continue
                seen.add(ref)
                collected.append(row)
        return collected

    def _paginate_city(self, city_ref: str, type_ref: str | None) -> list[dict] | None:
        rows: list[dict] = []
        for page in range(1, MAX_PAGES + 1):
            props: dict[str, str] = {
                "CityRef": city_ref,
                "Page": str(page),
                "Limit": str(PAGE_SIZE),
            }
            if type_ref:
                props["TypeOfWarehouseRef"] = type_ref
            chunk, ok = self._request_retry("Address", "getWarehouses", props)
            if not ok:
                return None
            if not chunk:
                break
            rows.extend(chunk)
            if len(chunk) < PAGE_SIZE:
                break
        return rows

    def _dedupe_mapped(self, rows: list[dict]) -> list[dict[str, Any]]:
        mapped: list[dict[str, Any]] = []
        seen: set[str] = set()
        for row in rows:
            item = self._map_warehouse(row)
            ref = item.get("ref") or ""
            if not ref or ref in seen:
                continue
            seen.add(ref)
            mapped.append(item)
        mapped.sort(key=lambda r: (r.get("point_type") != "warehouse", r.get("name") or ""))
        return mapped

    @staticmethod
    def _map_warehouse(row: dict) -> dict[str, Any]:
        description = row.get("Description") or ""
        category = str(row.get("CategoryOfWarehouse") or "")
        is_locker = "Поштомат" in description or category == "Postomat"
        return {
            "ref": row.get("Ref"),
            "name": description,
            "point_type": "locker" if is_locker else "warehouse",
        }
