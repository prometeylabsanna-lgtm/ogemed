from django.urls import path
from django.views.generic import RedirectView

from . import views

app_name = "catalog"

urlpatterns = [
    path("brendy/", views.BrandListView.as_view(), name="brands"),
    path("brendy/<slug:slug>/", views.BrandDetailView.as_view(), name="brand_detail"),
    path("katalog/", views.CatalogListView.as_view(), name="list"),
    path("katalog/<slug:slug>/", views.CategoryDetailView.as_view(), name="category"),
    path(
        "catalog/",
        RedirectView.as_view(pattern_name="catalog:list", query_string=True, permanent=False),
        name="list_alias",
    ),
    path("tovar/<slug:slug>/", views.ProductDetailView.as_view(), name="product_detail"),
    path("poshuk/", views.SearchView.as_view(), name="search"),
    path("api/poshuk/suggest/", views.search_suggest, name="search_suggest"),
]
