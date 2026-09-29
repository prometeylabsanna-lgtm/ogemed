from unittest.mock import patch

from django.core.cache import cache
from django.test import SimpleTestCase, override_settings

from apps.shipping.np_client import NovaPoshtaClient


@override_settings(
    NP_API_KEY="test-key",
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "np-wh-tests",
        }
    },
)
class NovaPoshtaWarehousesTests(SimpleTestCase):
    def setUp(self):
        cache.clear()

    def test_search_filters_full_city_catalog(self):
        raw_pages = {
            None: [
                [
                    {
                        "Ref": "w1",
                        "Description": "Відділення №1: вул. Тестова, 1",
                        "CategoryOfWarehouse": "Branch",
                    },
                    {
                        "Ref": "p1",
                        "Description": "Пункт №920: вул. Інша, 2",
                        "CategoryOfWarehouse": "Store",
                    },
                    {
                        "Ref": "l1",
                        "Description": 'Поштомат "Нова Пошта" №100: вул. Третя, 3',
                        "CategoryOfWarehouse": "Postomat",
                    },
                ]
            ]
        }

        def fake_request(model, method, props=None):
            props = props or {}
            if method == "getWarehouseTypes":
                return [], True
            if method == "getWarehouses":
                page = int(props.get("Page") or "1")
                chunks = raw_pages[None]
                if page > len(chunks):
                    return [], True
                return chunks[page - 1], True
            return [], False

        client = NovaPoshtaClient(api_key="test-key")
        with patch.object(client, "_request", side_effect=fake_request):
            all_items = client.list_city_warehouses("city-1")
            self.assertEqual(len(all_items), 3)

            branches = client.search_warehouses("city-1", "відд")
            self.assertEqual([r["ref"] for r in branches], ["w1"])

            points = client.search_warehouses("city-1", "пункт")
            self.assertEqual([r["ref"] for r in points], ["p1"])

            lockers = client.search_warehouses("city-1", "пошт")
            self.assertEqual(lockers[0]["point_type"], "locker")
            self.assertEqual(lockers[0]["ref"], "l1")

    def test_api_error_does_not_cache_partial(self):
        calls = {"n": 0}

        def fake_request(model, method, props=None):
            calls["n"] += 1
            if method == "getWarehouseTypes":
                return [], True
            if method == "getWarehouses":
                page = int((props or {}).get("Page") or "1")
                if page == 1:
                    return (
                        [
                            {
                                "Ref": "w1",
                                "Description": "Відділення №1",
                                "CategoryOfWarehouse": "Branch",
                            }
                        ]
                        * 500,
                        True,
                    )
                return [], False
            return [], False

        client = NovaPoshtaClient(api_key="test-key")
        with patch.object(client, "_request", side_effect=fake_request):
            self.assertEqual(client.list_city_warehouses("city-err"), [])
        # повторний виклик знову йде в API (не з кешу порожнечі після збою)
        with patch.object(client, "_request", side_effect=fake_request) as mocked:
            client.list_city_warehouses("city-err")
            self.assertGreater(mocked.call_count, 0)

    def test_paginates_until_short_page(self):
        def fake_request(model, method, props=None):
            props = props or {}
            if method == "getWarehouseTypes":
                return [{"Ref": "type-a"}], True
            if method == "getWarehouses":
                page = int(props.get("Page") or "1")
                if page == 1:
                    return (
                        [
                            {
                                "Ref": f"r{i}",
                                "Description": f"Відділення №{i}",
                                "CategoryOfWarehouse": "Branch",
                            }
                            for i in range(500)
                        ],
                        True,
                    )
                if page == 2:
                    return (
                        [
                            {
                                "Ref": "r500",
                                "Description": "Відділення №500",
                                "CategoryOfWarehouse": "Branch",
                            }
                        ],
                        True,
                    )
                return [], True
            return [], False

        client = NovaPoshtaClient(api_key="test-key")
        with patch.object(client, "_request", side_effect=fake_request):
            items = client.list_city_warehouses("city-big")
        self.assertEqual(len(items), 501)
