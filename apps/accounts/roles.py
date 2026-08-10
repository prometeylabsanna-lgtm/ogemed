"""Ролі доступу: група «Менеджер» — замовлення + каталог товарів."""
from __future__ import annotations

from django.contrib.auth.models import Group, Permission
from django.db.models import Q

MANAGER_GROUP_NAME = "Менеджер"

# App labels / model names, що бачить менеджер у адмінці.
MANAGER_APP_MODELS: dict[str, set[str]] = {
    "orders": {"order", "orderitem"},
    "catalog": {
        "product",
        "productvariant",
        "productimage",
        "category",
        "brand",
        "attribute",
        "attributevalue",
    },
    "cms": {"lead"},
}


def manager_permission_q() -> Q:
    q = Q()
    for app_label, models in MANAGER_APP_MODELS.items():
        q |= Q(content_type__app_label=app_label, content_type__model__in=models)
    return q


def ensure_manager_group() -> Group:
    """Створює/оновлює групу Менеджер з обмеженими правами (idempotent)."""
    group, _created = Group.objects.get_or_create(name=MANAGER_GROUP_NAME)
    perms = Permission.objects.filter(manager_permission_q()).select_related(
        "content_type"
    )
    # view + change для замовлень; повний CRUD для каталогу; view/change для лідів
    allowed = []
    for perm in perms:
        model = perm.content_type.model
        app = perm.content_type.app_label
        codename = perm.codename
        if app == "orders":
            if codename.startswith("view_") or codename.startswith("change_"):
                allowed.append(perm)
        elif app == "cms" and model == "lead":
            if codename.startswith("view_") or codename.startswith("change_"):
                allowed.append(perm)
        elif app == "catalog":
            if not codename.startswith("delete_"):
                allowed.append(perm)
            # delete дозволено лише для зображень / варіантів (редагування товару)
            elif model in {"productimage", "productvariant", "attributevalue"}:
                allowed.append(perm)
    group.permissions.set(allowed)
    return group


def assign_manager(user) -> Group:
    """Призначає користувачу роль менеджера (потрібен is_staff)."""
    group = ensure_manager_group()
    user.groups.add(group)
    if not user.is_staff:
        user.is_staff = True
        user.save(update_fields=["is_staff"])
    return group
