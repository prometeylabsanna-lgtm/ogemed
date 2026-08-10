from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.orders.models import DeliveryType, Order, OrderStatus, PaymentType

User = get_user_model()


class CabinetIDORTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner@example.com", email="owner@example.com", password="pass12345"
        )
        self.other = User.objects.create_user(
            username="other@example.com", email="other@example.com", password="pass12345"
        )
        self.order = Order.objects.create(
            user=self.owner,
            customer_name="Owner",
            customer_phone="+380501111111",
            delivery_type=DeliveryType.COURIER,
            payment_type=PaymentType.CASH_ON_DELIVERY,
            status=OrderStatus.PROCESSING,
            total=Decimal("10.00"),
            courier_city="Kyiv",
            courier_street="A",
        )

    def test_owner_sees_order(self):
        self.client.login(username="owner@example.com", password="pass12345")
        r = self.client.get(reverse("accounts:order_detail", kwargs={"pk": self.order.pk}))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Kyiv")
        self.assertContains(r, "Кур")  # Курʼєр / partial delivery label
        self.assertContains(r, "Оплата")

    def test_foreign_order_404(self):
        self.client.login(username="other@example.com", password="pass12345")
        r = self.client.get(reverse("accounts:order_detail", kwargs={"pk": self.order.pk}))
        self.assertEqual(r.status_code, 404)

    def test_register_and_login(self):
        r = self.client.post(
            reverse("accounts:register"),
            {
                "email": "new@example.com",
                "password1": "ComplexPass123!",
                "password2": "ComplexPass123!",
                "full_name": "New User",
            },
        )
        self.assertEqual(r.status_code, 302)
        self.assertTrue(User.objects.filter(email="new@example.com").exists())
        profile = User.objects.get(email="new@example.com").profile
        self.assertEqual(profile.full_name, "New User")

    def test_register_requires_valid_name_email_password(self):
        bad_name = self.client.post(
            reverse("accounts:register"),
            {
                "email": "bad@example.com",
                "password1": "ComplexPass123!",
                "password2": "ComplexPass123!",
                "full_name": "A",
            },
        )
        self.assertEqual(bad_name.status_code, 200)
        self.assertIn("full_name", bad_name.context["form"].errors)

        bad_email = self.client.post(
            reverse("accounts:register"),
            {
                "email": "not-an-email",
                "password1": "ComplexPass123!",
                "password2": "ComplexPass123!",
                "full_name": "Олена",
            },
        )
        self.assertEqual(bad_email.status_code, 200)
        self.assertIn("email", bad_email.context["form"].errors)

        mismatch = self.client.post(
            reverse("accounts:register"),
            {
                "email": "ok@example.com",
                "password1": "ComplexPass123!",
                "password2": "OtherPass123!",
                "full_name": "Олена",
            },
        )
        self.assertEqual(mismatch.status_code, 200)
        self.assertTrue(mismatch.context["form"].errors)
    def test_login_respects_next(self):
        next_url = reverse("accounts:profile")
        r = self.client.post(
            reverse("accounts:login") + f"?next={next_url}",
            {
                "username": "owner@example.com",
                "password": "pass12345",
                "next": next_url,
            },
        )
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r.url, next_url)

    def test_password_change(self):
        self.client.login(username="owner@example.com", password="pass12345")
        bad = self.client.post(
            reverse("accounts:password_change"),
            {
                "old_password": "wrong",
                "new_password1": "NewComplexPass123!",
                "new_password2": "NewComplexPass123!",
            },
        )
        self.assertEqual(bad.status_code, 200)
        self.assertTrue(bad.context["form"].errors)

        ok = self.client.post(
            reverse("accounts:password_change"),
            {
                "old_password": "pass12345",
                "new_password1": "NewComplexPass123!",
                "new_password2": "NewComplexPass123!",
            },
        )
        self.assertEqual(ok.status_code, 302)
        self.assertEqual(ok.url, reverse("accounts:password_change_done"))
        self.client.logout()
        self.assertTrue(
            self.client.login(username="owner@example.com", password="NewComplexPass123!")
        )
