"""Масові дії для товарів в адмінці."""
from __future__ import annotations

from django.contrib import admin, messages
from django.db.models import QuerySet
from django.http import HttpRequest


@admin.action(description="Позначити як хіт")
def mark_as_hit(modeladmin, request: HttpRequest, queryset: QuerySet) -> None:
    updated = queryset.update(is_hit=True)
    modeladmin.message_user(
        request, f"Позначено хітом: {updated}", messages.SUCCESS
    )


@admin.action(description="Зняти позначку «хіт»")
def unmark_as_hit(modeladmin, request: HttpRequest, queryset: QuerySet) -> None:
    updated = queryset.update(is_hit=False)
    modeladmin.message_user(
        request, f"Знято «хіт»: {updated}", messages.SUCCESS
    )


@admin.action(description="Позначити як новинку")
def mark_as_new(modeladmin, request: HttpRequest, queryset: QuerySet) -> None:
    updated = queryset.update(is_new=True)
    modeladmin.message_user(
        request, f"Позначено новинкою: {updated}", messages.SUCCESS
    )


@admin.action(description="Зняти позначку «новинка»")
def unmark_as_new(modeladmin, request: HttpRequest, queryset: QuerySet) -> None:
    updated = queryset.update(is_new=False)
    modeladmin.message_user(
        request, f"Знято «новинка»: {updated}", messages.SUCCESS
    )


@admin.action(description="Позначити як акцію")
def mark_as_sale(modeladmin, request: HttpRequest, queryset: QuerySet) -> None:
    updated = queryset.update(is_sale=True)
    modeladmin.message_user(
        request, f"Позначено акцією: {updated}", messages.SUCCESS
    )


@admin.action(description="Зняти позначку «акція»")
def unmark_as_sale(modeladmin, request: HttpRequest, queryset: QuerySet) -> None:
    updated = queryset.update(is_sale=False)
    modeladmin.message_user(
        request, f"Знято «акція»: {updated}", messages.SUCCESS
    )


@admin.action(description="Зробити активними")
def mark_published(modeladmin, request: HttpRequest, queryset: QuerySet) -> None:
    from apps.catalog.models import Product

    updated = queryset.update(status=Product.Status.ACTIVE)
    modeladmin.message_user(
        request, f"Зроблено активними: {updated}", messages.SUCCESS
    )


@admin.action(description="Зробити неактивними")
def mark_draft(modeladmin, request: HttpRequest, queryset: QuerySet) -> None:
    from apps.catalog.models import Product

    updated = queryset.update(status=Product.Status.INACTIVE)
    modeladmin.message_user(
        request, f"Зроблено неактивними: {updated}", messages.SUCCESS
    )


PRODUCT_ADMIN_ACTIONS = (
    mark_as_hit,
    unmark_as_hit,
    mark_as_new,
    unmark_as_new,
    mark_as_sale,
    unmark_as_sale,
    mark_published,
    mark_draft,
)
