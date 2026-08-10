from django.urls import path

from . import views

app_name = "cart"

urlpatterns = [
    path("koshyk/", views.CartDetailView.as_view(), name="detail"),
    path("koshyk/add/", views.cart_add, name="add"),
    path("koshyk/update/", views.cart_update, name="update"),
    path("koshyk/remove/", views.cart_remove, name="remove"),
    path("koshyk/count/", views.cart_count_partial, name="count"),
]
