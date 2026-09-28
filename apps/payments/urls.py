from django.urls import path

from . import views

app_name = "payments"

urlpatterns = [
    path("payments/monopay/callback/", views.monopay_callback, name="monopay_callback"),
    path("payments/monopay/retry/", views.monopay_retry, name="monopay_retry"),
]
