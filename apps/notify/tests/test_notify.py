from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase, override_settings

from apps.notify.services import notify_new_order, send_viber
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
    @patch("apps.notify.services.send_telegram")
    @patch("apps.notify.services.send_viber")
    def test_status_transition_emails_customer(self, _viber, _tg, send_email):
        with self.captureOnCommitCallbacks(execute=True):
            OrderStatusService.transition(self.order, OrderStatus.SHIPPED, notify=True)
        self.assertTrue(send_email.called)
        customer_calls = [
            c for c in send_email.call_args_list if c[0][0] == "client@example.com"
        ]
        self.assertEqual(len(customer_calls), 1)
        args, _kwargs = customer_calls[0]
        self.assertIn(self.order.order_number, args[1])
        self.assertIn("Відправлено", args[2])

    @override_settings(RESEND_API_KEY="test-key", FROM_EMAIL="shop@example.com")
    @patch("apps.notify.services.send_email")
    @patch("apps.notify.services.send_telegram")
    @patch("apps.notify.services.send_viber")
    def test_status_notifies_owner_messengers(self, send_viber_mock, send_tg, _email):
        with self.captureOnCommitCallbacks(execute=True):
            OrderStatusService.transition(self.order, OrderStatus.SHIPPED, notify=True)
        send_tg.assert_called_once()
        send_viber_mock.assert_called_once()
        self.assertIn(self.order.order_number, send_viber_mock.call_args[0][0])
        self.assertIn("Відправлено", send_viber_mock.call_args[0][0])

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

    @override_settings(RESEND_API_KEY="test-key", FROM_EMAIL="shop@example.com")
    @patch("apps.notify.services.send_email")
    @patch("apps.notify.services.send_telegram")
    @patch("apps.notify.services.send_viber")
    def test_new_order_fop_includes_requisites(self, _viber, _tg, send_email):
        from apps.core.models import SiteSettings

        site = SiteSettings.load()
        site.fop_recipient_name = "ФОП Тестова"
        site.fop_iban = "UA111122223333444455556666777"
        site.fop_edrpou = "1122334455"
        site.save()
        self.order.payment_type = PaymentType.FOP_CARD
        self.order.save(update_fields=["payment_type"])
        with self.captureOnCommitCallbacks(execute=True):
            notify_new_order(self.order)
        html = send_email.call_args_list[-1][0][2]
        self.assertIn("Реквізити для оплати", html)
        self.assertIn("ФОП Тестова", html)
        self.assertIn(f"Оплата замовлення №{self.order.order_number}", html)

    def test_notify_false_skips_email(self):
        with patch("apps.notify.services.notify_order_status_changed") as mocked:
            OrderStatusService.transition(
                self.order, OrderStatus.SHIPPED, notify=False
            )
            mocked.assert_not_called()

    @override_settings(RESEND_API_KEY="test-key", FROM_EMAIL="shop@example.com")
    @patch("apps.notify.services.send_email")
    @patch("apps.notify.services.send_telegram")
    @patch("apps.notify.services.send_viber")
    def test_status_notify_without_customer_email_still_owner(
        self, send_viber_mock, send_tg, send_email
    ):
        self.order.customer_email = ""
        self.order.save(update_fields=["customer_email"])
        with self.captureOnCommitCallbacks(execute=True):
            OrderStatusService.transition(self.order, OrderStatus.SHIPPED, notify=True)
        send_tg.assert_called_once()
        send_viber_mock.assert_called_once()
        for call in send_email.call_args_list:
            self.assertNotEqual(call[0][0], "")

    @override_settings(
        TURBOSMS_API_TOKEN="tok",
        TURBOSMS_OWNER_PHONE="380664247233",
        TURBOSMS_VIBER_SENDER="Ogemed",
    )
    @patch("apps.notify.services.urlrequest.urlopen")
    def test_send_viber_turbosms_payload(self, urlopen):
        class _Resp:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def read(self):
                return b"{}"

        urlopen.return_value = _Resp()
        send_viber("Тест замовлення")
        req = urlopen.call_args[0][0]
        self.assertEqual(req.full_url, "https://api.turbosms.ua/message/send.json")
        self.assertEqual(req.get_header("Authorization"), "Bearer tok")
        body = req.data.decode()
        self.assertIn("380664247233", body)
        self.assertIn("Ogemed", body)
        self.assertIn("is_transactional", body)
