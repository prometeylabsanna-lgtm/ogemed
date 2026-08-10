from django.urls import path

from . import views

app_name = "shipping"

urlpatterns = [
    path("api/np/cities/", views.np_cities, name="np_cities"),
    path("api/np/warehouses/", views.np_warehouses, name="np_warehouses"),
]
