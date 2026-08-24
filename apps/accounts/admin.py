from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from unfold.admin import ModelAdmin, StackedInline
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from apps.core.admin_filters import DropdownFiltersMixin, UkBooleanDropdownFilter

from .models import Profile

User = get_user_model()


class ProfileInline(StackedInline):
    model = Profile
    can_delete = False


class UserAdmin(DropdownFiltersMixin, DjangoUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    inlines = [ProfileInline]
    list_display = ("username", "email", "is_staff", "is_active", "date_joined")
    list_filter = (
        ("is_active", UkBooleanDropdownFilter),
        ("is_staff", UkBooleanDropdownFilter),
        ("is_superuser", UkBooleanDropdownFilter),
    )
    search_fields = ("username", "email")


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(Profile)
class ProfileAdmin(ModelAdmin):
    list_display = ("user", "full_name", "phone")
    search_fields = ("full_name", "phone", "user__email")
