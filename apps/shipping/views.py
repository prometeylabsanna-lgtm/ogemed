from django.http import JsonResponse
from django.views.decorators.http import require_GET

from .np_client import NovaPoshtaClient


@require_GET
def np_cities(request):
    q = (request.GET.get("q") or "").strip()
    if len(q) < 2:
        return JsonResponse({"results": []})
    client = NovaPoshtaClient()
    return JsonResponse({"results": client.search_cities(q)})


@require_GET
def np_warehouses(request):
    city_ref = (request.GET.get("city_ref") or "").strip()
    q = (request.GET.get("q") or "").strip()
    warm = (request.GET.get("warm") or "").strip() in ("1", "true", "yes")
    if not city_ref:
        return JsonResponse({"results": []})

    client = NovaPoshtaClient()
    if warm:
        items = client.list_city_warehouses(city_ref)
        return JsonResponse({"ok": True, "count": len(items)})

    if len(q) < 2:
        return JsonResponse({"results": []})
    return JsonResponse({"results": client.search_warehouses(city_ref, q)})
