from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase, override_settings

from apps.notify.services import notify_new_order, notify_order_status_changed
from apps.orders.models import DeliveryType, Order, OrderStatus, PaymentType
from apps.orders.services_status import OrderStatusService


class NotifyTemplatesTests(TestCase):
    def setUp(self):
        self.order = Order.objects.create(
            customer_name="Тест",
            customer_phone="+380501112233",
            customer_email="client@example.com",
            delivery_type=DeliveryType.COURIER,
            payment_type=PaymentType.CASH_ON_DELIVERY,
            status=OrderStatus.PROCESSING,
            total=Decimal("199.00"),
            courier_city="Київ",
        )

    @override_settings(RESEND_API_KEY="", FROM_EMAIL="shop@example.com")
    def test_status_notify_skips_without_api_key(self):
        OrderStatusService.transition(self.order, OrderStatus.SHIPPED, notify=True)
        self.assertEqual(self.order.status, OrderStatus.SHIPPED)

    @override_settings(RESEND_API_KEY="test-key", FROM_EMAIL="shop@example.com")
    @patch("apps.notify.services.send_email")
    def test_status_transition_emails_customer(self, send_email):
        with self.captureOnCommitCallbacks(execute=True):
            OrderStatusService.transition(self.order, OrderStatus.SHIPPED, notify=True)
        send_email.assert_called_once()
        args, _kwargs = send_email.call_args
        self.assertEqual(args[0], "client@example.com")
        self.assertIn(self.order.order_number, args[1])
        self.assertIn("Відправлено", args[2])

    @override_settings(RESEND_API_KEY="test-key", FROM_EMAIL="shop@example.com")
    @patch("apps.notify.services.send_email")
    @patch("apps.notify.services.send_telegram")
    @patch("apps.notify.services.send_viber")
    def test_new_order_renders_templates(self, _viber, _tg, send_email):
        with self.captureOnCommitCallbacks(execute=True):
            notify_new_order(self.order)
        self.assertTrue(send_email.called)
        html = send_email.call_args_list[0][0][2]
        self.assertIn(self.order.order_number, html)

    def test_notify_false_skips_email(self):
        with patch("apps.notify.services.notify_order_status_changed") as mocked:
            OrderStatusService.transition(
                self.order, OrderStatus.SHIPPED, notify=False
            )
            mocked.assert_not_called()

    def test_status_notify_without_email_noop(self):
        self.order.customer_email = ""
        self.order.save(update_fields=["customer_email"])
        with patch("apps.notify.services.send_email") as send_email:
            notify_order_status_changed(
                self.order, previous_status=OrderStatus.PROCESSING
            )
            send_email.assert_not_called()
