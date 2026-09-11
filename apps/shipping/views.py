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
    # Search from 2+ chars — avoid dumping full city lists into autocomplete.
    if not city_ref or len(q) < 2:
        return JsonResponse({"results": []})
    client = NovaPoshtaClient()
    return JsonResponse({"results": client.get_warehouses(city_ref, q)})
