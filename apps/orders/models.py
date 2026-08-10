import secrets
import uuid
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class OrderStatus(models.TextChoices):
    NEW = "new", _("Нове")
    AWAITING_PAYMENT = "awaiting_payment", _("Очікує оплати")
    PAID = "paid", _("Оплачено")
    PROCESSING = "processing", _("В обробці")
    SHIPPED = "shipped", _("Відправлено")
    DONE = "done", _("Виконано")
    CANCELLED = "cancelled", _("Скасовано")


class DeliveryType(models.TextChoices):
    NOVA_POSHTA = "nova_poshta", _("Нова Пошта")
    COURIER = "courier", _("Курʼєр")


class PaymentType(models.TextChoices):
    LIQPAY = "liqpay", _("LiqPay")
    CASH_ON_DELIVERY = "cash_on_delivery", _("Оплата при отриманні")


class NPPointType(models.TextChoices):
    WAREHOUSE = "warehouse", _("Відділення")
    LOCKER = "locker", _("Поштомат")


def generate_order_number() -> str:
    return timezone.now().strftime("%y%m%d") + secrets.token_hex(3).upper()


def generate_access_token() -> str:
    return uuid.uuid4().hex


class Order(models.Model):
    order_number = models.CharField(
        _("Номер"), max_length=32, unique=True, default=generate_order_number, editable=False
    )
    access_token = models.CharField(
        _("Токен доступу"),
        max_length=64,
        unique=True,
        default=generate_access_token,
        editable=False,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
        verbose_name=_("Користувач"),
    )
    status = models.CharField(
        _("Статус"),
        max_length=32,
        choices=OrderStatus.choices,
        default=OrderStatus.NEW,
        db_index=True,
    )
    customer_name = models.CharField(_("ПІБ"), max_length=255)
    customer_phone = models.CharField(_("Телефон"), max_length=32)
    customer_email = models.EmailField(_("Email"), blank=True)
    delivery_type = models.CharField(
        _("Доставка"), max_length=32, choices=DeliveryType.choices
    )
    np_city_ref = models.CharField(max_length=64, blank=True)
    np_city_name = models.CharField(max_length=255, blank=True)
    np_warehouse_ref = models.CharField(max_length=64, blank=True)
    np_warehouse_name = models.CharField(max_length=255, blank=True)
    np_point_type = models.CharField(
        max_length=32, choices=NPPointType.choices, blank=True
    )
    courier_city = models.CharField(max_length=120, blank=True)
    courier_street = models.CharField(max_length=255, blank=True)
    courier_building = models.CharField(max_length=64, blank=True)
    courier_apartment = models.CharField(max_length=64, blank=True)
    courier_comment = models.TextField(blank=True)
    payment_type = models.CharField(
        _("Оплата"), max_length=32, choices=PaymentType.choices
    )
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Замовлення")
        verbose_name_plural = _("Замовлення")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.order_number


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items", verbose_name=_("Замовлення")
    )
    product = models.ForeignKey(
        "catalog.Product",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_items",
    )
    variant = models.ForeignKey(
        "catalog.ProductVariant",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_items",
    )
    name = models.CharField(_("Назва"), max_length=255)
    sku = models.CharField(_("Артикул"), max_length=64)
    variant_label = models.CharField(_("Модифікація"), max_length=120, blank=True)
    unit_price = models.DecimalField(_("Ціна"), max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(_("Кількість"), default=1)
    line_total = models.DecimalField(_("Сума"), max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = _("Позиція замовлення")
        verbose_name_plural = _("Позиції замовлення")

    def __str__(self) -> str:
        return f"{self.name} × {self.quantity}"
