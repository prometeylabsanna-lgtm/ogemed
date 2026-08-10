from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from apps.accounts.roles import MANAGER_GROUP_NAME, assign_manager, ensure_manager_group

User = get_user_model()


class ManagerRoleTests(TestCase):
    def test_ensure_manager_group_permissions(self):
        group = ensure_manager_group()
        self.assertEqual(group.name, MANAGER_GROUP_NAME)
        codenames = set(group.permissions.values_list("codename", flat=True))
        self.assertIn("view_order", codenames)
        self.assertIn("change_order", codenames)
        self.assertIn("change_product", codenames)
        self.assertNotIn("delete_order", codenames)
        self.assertNotIn("add_user", codenames)

    def test_manager_can_open_order_admin(self):
        user = User.objects.create_user(
            username="mgr@example.com",
            email="mgr@example.com",
            password="pass12345",
        )
        assign_manager(user)
        self.assertTrue(user.is_staff)
        client = Client()
        self.assertTrue(client.login(username="mgr@example.com", password="pass12345"))
        r = client.get("/admin/orders/order/")
        self.assertEqual(r.status_code, 200)

    def test_manager_cannot_open_sitesettings(self):
        user = User.objects.create_user(
            username="mgr2@example.com",
            email="mgr2@example.com",
            password="pass12345",
        )
        assign_manager(user)
        client = Client()
        client.login(username="mgr2@example.com", password="pass12345")
        r = client.get("/admin/core/sitesettings/")
        self.assertIn(r.status_code, (403, 302))
