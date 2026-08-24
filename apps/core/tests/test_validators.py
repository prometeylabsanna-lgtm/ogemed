from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from apps.cms.lead_views import LeadForm
from apps.cms.models import Lead
from apps.core.validators import (
    validate_email,
    validate_message,
    validate_name,
    validate_phone,
)
from django.core.exceptions import ValidationError


class ValidatorsTests(SimpleTestCase):
    def test_name_rules(self):
        self.assertEqual(validate_name("  Олег-Марія  "), "Олег-Марія")
        with self.assertRaises(ValidationError):
            validate_name("Oleg2")
        with self.assertRaises(ValidationError):
            validate_name("a")
        with self.assertRaises(ValidationError):
            validate_name("https://spam.ua")

    def test_phone_ua(self):
        self.assertEqual(validate_phone("0501112233"), "+380501112233")
        self.assertEqual(validate_phone("+380 50 111 22 33"), "+380501112233")
        with self.assertRaises(ValidationError):
            validate_phone("12345")

    def test_email_normalize(self):
        self.assertEqual(validate_email("  A@B.CD "), "a@b.cd")
        self.assertEqual(validate_email("", required=False), "")
        with self.assertRaises(ValidationError):
            validate_email("not-email")

    def test_message_optional_and_sanitize(self):
        self.assertEqual(validate_message("", required=False), "")
        with self.assertRaises(ValidationError):
            validate_message("коротко")
        cleaned = validate_message("Привіт <script>x</script> друзі мої!")
        self.assertNotIn("<", cleaned)
        self.assertIn("Привіт", cleaned)


class LeadFormValidationTests(TestCase):
    def test_callback_requires_name_and_valid_phone(self):
        form = LeadForm(
            data={
                "lead_type": Lead.LeadType.CALLBACK,
                "name": "",
                "phone": "123",
                "email": "",
                "message": "",
                "website": "",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)
        self.assertIn("phone", form.errors)

    def test_callback_accepts_optional_message_empty(self):
        form = LeadForm(
            data={
                "lead_type": Lead.LeadType.CALLBACK,
                "name": "Олена",
                "phone": "+380501112233",
                "email": "test@example.com",
                "message": "",
                "website": "",
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["phone"], "+380501112233")
        self.assertEqual(form.cleaned_data["email"], "test@example.com")

    def test_lead_create_rejects_invalid_phone(self):
        r = self.client.post(
            reverse("cms:lead_create"),
            {
                "lead_type": Lead.LeadType.CALLBACK,
                "name": "Олена",
                "phone": "99",
                "website": "",
            },
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(r.status_code, 422)
        self.assertContains(r, "data-field-error-for", status_code=422)
        self.assertContains(r, "номер", status_code=422)
