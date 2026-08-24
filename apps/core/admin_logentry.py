"""Адмінка журналу дій (LogEntry) — сторінка «Недавні дії»."""
from __future__ import annotations

from django.contrib import admin
from django.contrib.admin.models import DELETION, LogEntry
from django.utils.html import format_html
from unfold.admin import ModelAdmin

from apps.core.admin_filters import (
    DropdownFiltersMixin,
    UkActionFlagDropdownFilter,
    UkRelatedDropdownFilter,
)


@admin.register(LogEntry)
class LogEntryAdmin(DropdownFiltersMixin, ModelAdmin):
    list_display = (
        "action_time",
        "user",
        "content_type",
        "object_link",
        "action_label",
    )
    list_filter = (
        ("user", UkRelatedDropdownFilter),
        ("content_type", UkRelatedDropdownFilter),
        ("action_flag", UkActionFlagDropdownFilter),
    )
    search_fields = ("object_repr", "change_message", "user__username")
    search_help_text = "Пошук…"
    date_hierarchy = "action_time"
    ordering = ("-action_time",)
    list_per_page = 50
    readonly_fields = (
        "action_time",
        "user",
        "content_type",
        "object_id",
        "object_repr",
        "action_flag",
        "change_message",
    )

    @admin.display(description="Обʼєкт")
    def object_link(self, obj: LogEntry):
        if obj.action_flag == DELETION or not obj.get_admin_url():
            return obj.object_repr
        return format_html('<a href="{}">{}</a>', obj.get_admin_url(), obj.object_repr)

    @admin.display(description="Дія")
    def action_label(self, obj: LogEntry) -> str:
        if obj.is_addition:
            return "Додано"
        if obj.is_change:
            return "Змінено"
        if obj.is_deletion:
            return "Видалено"
        return "—"

    def has_add_permission(self, request) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return False

    def has_module_permission(self, request) -> bool:
        # не показувати групу Administration у app_list — лише через сайдбар
        return False

    def has_view_permission(self, request, obj=None) -> bool:
        return bool(request.user.is_staff)

    def has_change_permission(self, request, obj=None) -> bool:
        # лише перегляд списку / деталі (поля readonly)
        return bool(request.user.is_staff)
