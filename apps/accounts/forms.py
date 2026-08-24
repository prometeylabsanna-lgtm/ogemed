from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.utils.translation import gettext_lazy as _

from apps.core.validators import (
    NAME_MAX,
    validate_email,
    validate_name,
    validate_password_register,
    validate_phone,
)
from apps.orders.forms import PHONE_ATTRS

from .models import Profile

User = get_user_model()


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(
            attrs={
                "autocomplete": "email",
                "inputmode": "email",
                "placeholder": _("diana.k@example.org"),
                "data-validate": "email",
            }
        ),
    )
    password = forms.CharField(
        label=_("Пароль"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "current-password",
                "placeholder": _("Ваш пароль"),
                "data-validate": "password_login",
            }
        ),
    )

    def clean_username(self):
        return validate_email(self.cleaned_data.get("username"), required=True)


class RegisterForm(UserCreationForm):
    full_name = forms.CharField(
        label=_("Імʼя"),
        max_length=NAME_MAX,
        required=True,
        widget=forms.TextInput(
            attrs={
                "autocomplete": "name",
                "placeholder": _("Ваше імʼя"),
                "data-validate": "name",
            }
        ),
    )
    email = forms.EmailField(
        label=_("Email"),
        required=True,
        widget=forms.EmailInput(
            attrs={
                "autocomplete": "email",
                "inputmode": "email",
                "placeholder": _("diana.k@example.org"),
                "data-validate": "email",
            }
        ),
    )
    password1 = forms.CharField(
        label=_("Пароль"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "new-password",
                "placeholder": _("Мінімум 8 символів"),
                "data-validate": "password",
            }
        ),
    )
    password2 = forms.CharField(
        label=_("Підтвердження пароля"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "new-password",
                "placeholder": _("Повторіть пароль"),
                "data-validate": "password_confirm",
                "data-validate-match": "password1",
            }
        ),
    )

    class Meta:
        model = User
        fields = ("email",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.order_fields(["full_name", "email", "password1", "password2"])

    def clean_full_name(self):
        return validate_name(self.cleaned_data.get("full_name"), required=True)

    def clean_email(self):
        email = validate_email(self.cleaned_data.get("email"), required=True)
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(_("Користувач з таким email вже існує"))
        return email

    def clean_password1(self):
        return validate_password_register(
            self.cleaned_data.get("password1"),
            email=self.data.get("email") or "",
        )

    def clean(self):
        cleaned = super().clean()
        password1 = cleaned.get("password1")
        password2 = cleaned.get("password2")
        if password1 and password2 and password1 != password2:
            self.add_error(
                "password2",
                _(
                    "Введені паролі не збігаються. "
                    "Перевірте правильність повторного вводу."
                ),
            )
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        email = self.cleaned_data["email"].lower().strip()
        user.username = email
        user.email = email
        if commit:
            user.save()
            Profile.objects.update_or_create(
                user=user,
                defaults={
                    "full_name": self.cleaned_data.get("full_name", ""),
                    "phone": "",
                },
            )
        return user


class ProfileForm(forms.ModelForm):
    email = forms.EmailField(
        label=_("Email"),
        required=True,
        widget=forms.EmailInput(
            attrs={
                "autocomplete": "email",
                "inputmode": "email",
                "data-validate": "email",
            }
        ),
    )

    class Meta:
        model = Profile
        fields = (
            "full_name",
            "phone",
            "default_city",
            "default_street",
            "default_building",
            "default_apartment",
        )
        widgets = {
            "full_name": forms.TextInput(
                attrs={
                    "autocomplete": "name",
                    "data-validate": "name_optional",
                    "maxlength": str(NAME_MAX),
                }
            ),
            "phone": forms.TextInput(attrs=PHONE_ATTRS),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        self.fields["email"].initial = self.user.email
        self.fields["full_name"].required = False
        self.fields["phone"].required = False
        phone_widget = self.fields["phone"].widget
        phone_widget.attrs = {**phone_widget.attrs, "data-validate": "phone_optional"}

    def clean_full_name(self):
        return validate_name(self.cleaned_data.get("full_name"), required=False)

    def clean_phone(self):
        return validate_phone(self.cleaned_data.get("phone"), required=False)

    def clean_email(self):
        return validate_email(self.cleaned_data.get("email"), required=True)

    def save(self, commit=True):
        profile = super().save(commit=False)
        email = self.cleaned_data["email"].lower().strip()
        self.user.email = email
        self.user.username = email
        if commit:
            self.user.save(update_fields=["email", "username"])
            profile.save()
        return profile
