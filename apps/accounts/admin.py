"""Адмінка користувачів: прості поля, без груп/дозволів/профілю."""
from __future__ import annotations

from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.forms import UserChangeForm as DjangoUserChangeForm
from django.contrib.auth.forms import UserCreationForm as DjangoUserCreationForm
from django.contrib.auth.password_validation import validate_password
from unfold.admin import ModelAdmin
from unfold.widgets import INPUT_CLASSES, UnfoldBooleanWidget

from apps.core.admin_field_hints import AdminFieldHintsMixin
from apps.core.admin_filters import DropdownFiltersMixin, UkBooleanDropdownFilter

from .models import Profile
from .roles import MANAGER_GROUP_NAME, assign_manager, ensure_manager_group

User = get_user_model()


def _password_widget(*, autocomplete: str) -> forms.PasswordInput:
    return forms.PasswordInput(
        attrs={
            "autocomplete": autocomplete,
            "class": " ".join(INPUT_CLASSES),
        },
        render_value=False,
    )


class AdminUserCreationForm(DjangoUserCreationForm):
    class Meta(DjangoUserCreationForm.Meta):
        model = User
        fields = ("username", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].label = "Пароль"
        self.fields["password2"].label = "Підтвердження пароля"
        self.fields["password1"].widget = _password_widget(autocomplete="new-password")
        self.fields["password2"].widget = _password_widget(autocomplete="new-password")
        if "email" in self.fields:
            self.fields["email"].required = False


class AdminUserChangeForm(DjangoUserChangeForm):
    """Замість хешу — поля для нового пароля (опційно)."""

    password1 = forms.CharField(
        label="Новий пароль",
        required=False,
        strip=False,
        widget=_password_widget(autocomplete="new-password"),
        help_text="Залиште порожнім, якщо пароль змінювати не потрібно.",
    )
    password2 = forms.CharField(
        label="Підтвердження пароля",
        required=False,
        strip=False,
        widget=_password_widget(autocomplete="new-password"),
    )
    is_manager = forms.BooleanField(
        label="Менеджер",
        required=False,
        widget=UnfoldBooleanWidget(),
        help_text="Доступ до замовлень і каталогу (без ручного вибору груп).",
    )

    class Meta(DjangoUserChangeForm.Meta):
        model = User
        fields = (
            "username",
            "email",
            "is_active",
            "is_staff",
            "is_superuser",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop("password", None)
        if self.instance and self.instance.pk:
            self.fields["is_manager"].initial = self.instance.groups.filter(
                name=MANAGER_GROUP_NAME
            ).exists()

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1") or ""
        p2 = cleaned.get("password2") or ""
        if not p1 and not p2:
            return cleaned
        if p1 != p2:
            self.add_error("password2", "Паролі не збігаються.")
        elif p1:
            validate_password(p1, self.instance)
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        p1 = self.cleaned_data.get("password1") or ""
        if p1:
            user.set_password(p1)
        if self.cleaned_data.get("is_manager") and not user.is_staff:
            user.is_staff = True
        if commit:
            user.save()
            self.save_m2m()
            self._sync_manager_role(user)
        return user

    def _sync_manager_role(self, user) -> None:
        ensure_manager_group()
        if self.cleaned_data.get("is_manager"):
            assign_manager(user)
            return
        group = user.groups.filter(name=MANAGER_GROUP_NAME).first()
        if group is not None:
            user.groups.remove(group)


class UserAdmin(AdminFieldHintsMixin, DropdownFiltersMixin, DjangoUserAdmin, ModelAdmin):
    form = AdminUserChangeForm
    add_form = AdminUserCreationForm
    inlines = []
    filter_horizontal = ()
    list_display = ("username", "email", "is_staff", "is_active", "date_joined")
    list_filter = (
        ("is_active", UkBooleanDropdownFilter),
        ("is_staff", UkBooleanDropdownFilter),
        ("is_superuser", UkBooleanDropdownFilter),
    )
    search_fields = ("username", "email")
    ordering = ("username",)
    readonly_fields = ()
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "username",
                    "email",
                    "password1",
                    "password2",
                ),
            },
        ),
        (
            "Доступ",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_manager",
                    "is_superuser",
                ),
            },
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                ),
            },
        ),
    )

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return self.fieldsets

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        sync = getattr(form, "_sync_manager_role", None)
        if callable(sync):
            sync(obj)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(Profile)
class ProfileAdmin(AdminFieldHintsMixin, ModelAdmin):
    list_display = ("user", "full_name", "phone")
    search_fields = ("full_name", "phone", "user__email")

    def has_module_permission(self, request) -> bool:
        return False
