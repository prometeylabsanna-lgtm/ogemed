from django.urls import path

from . import views

app_name = "orders"

urlpatterns = [
    path("oformlennya/", views.CheckoutView.as_view(), name="checkout"),
    path("dyakuyemo/", views.ThankYouView.as_view(), name="thank_you"),
]
