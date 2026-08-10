from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class PaymentAttempt(models.Model):
    class Status(models.TextChoices):
        CREATED = "created", _("Створено")
        SUCCESS = "success", _("Успіх")
        FAILURE = "failure", _("Помилка")
        SANDBOX = "sandbox", _("Sandbox")

    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="payment_attempts",
        verbose_name=_("Замовлення"),
    )
    provider = models.CharField(max_length=32, default="liqpay")
    provider_order_id = models.CharField(max_length=64, blank=True, db_index=True)
    payment_id = models.CharField(max_length=64, blank=True)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.CREATED)
    idempotency_key = models.CharField(max_length=120, unique=True, null=True, blank=True)
    raw_payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Спроба оплати")
        verbose_name_plural = _("Спроби оплати")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.provider}:{self.provider_order_id}:{self.status}"
