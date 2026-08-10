from django.urls import path

from . import views

app_name = "payments"

urlpatterns = [
    path("payments/liqpay/callback/", views.liqpay_callback, name="liqpay_callback"),
    path("payments/liqpay/return/", views.liqpay_return, name="liqpay_return"),
    path("payments/liqpay/retry/", views.liqpay_retry, name="liqpay_retry"),
]
