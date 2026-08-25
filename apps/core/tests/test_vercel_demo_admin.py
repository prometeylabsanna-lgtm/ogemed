"""Vercel demo admin must not rotate password hash on every cold start."""
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from config.vercel_sqlite import ensure_vercel_demo_admin


class VercelDemoAdminTests(TestCase):
    @patch("config.vercel_sqlite.is_vercel_lambda", return_value=True)
    @patch.dict("os.environ", {"DEMO_ADMIN_PASSWORD": "stable-pass"}, clear=False)
    def test_ensure_does_not_rotate_hash_when_password_matches(self, _mock):
        User = get_user_model()
        ensure_vercel_demo_admin()
        user = User.objects.get(username="admin")
        hash_before = user.password

        ensure_vercel_demo_admin()
        user.refresh_from_db()
        self.assertEqual(user.password, hash_before)
        self.assertTrue(user.check_password("stable-pass"))

    @patch("config.vercel_sqlite.is_vercel_lambda", return_value=True)
    @patch.dict("os.environ", {"DEMO_ADMIN_PASSWORD": "new-pass"}, clear=False)
    def test_ensure_updates_when_env_password_changes(self, _mock):
        User = get_user_model()
        ensure_vercel_demo_admin()
        user = User.objects.get(username="admin")
        # env already new-pass from patch; force old hash then re-run with same env
        user.set_password("old-pass")
        user.save(update_fields=["password"])
        ensure_vercel_demo_admin()
        user.refresh_from_db()
        self.assertTrue(user.check_password("new-pass"))
