from django.core.management.base import BaseCommand

from apps.accounts.roles import MANAGER_GROUP_NAME, ensure_manager_group


class Command(BaseCommand):
    help = "Створює/оновлює групу «Менеджер» (замовлення + товари)."

    def handle(self, *args, **options):
        group = ensure_manager_group()
        count = group.permissions.count()
        self.stdout.write(
            self.style.SUCCESS(
                f"Група «{MANAGER_GROUP_NAME}»: {count} permissions."
            )
        )
