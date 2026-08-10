import re

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.utils.translation import gettext_lazy as _

from apps.orders.forms import PHONE_ATTRS

from .models import Profile

User = get_user_model()

_NAME_RE = re.compile(
    r"^[A-Za-zА-Яа-яЁёІіЇїЄєҐґʼ'`’.\-\s]+$",
    re.UNICODE,
)
_EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(
            attrs={
                "autocomplete": "email",
                "inputmode": "email",
                "placeholder": _("diana.k@example.org"),
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
            }
        ),
    )


class RegisterForm(UserCreationForm):
    full_name = forms.CharField(
        label=_("Імʼя"),
        max_length=255,
        required=True,
        widget=forms.TextInput(
            attrs={
                "autocomplete": "name",
                "placeholder": _("Ваше імʼя"),
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
        name = (self.cleaned_data.get("full_name") or "").strip()
        name = re.sub(r"\s+", " ", name)
        if len(name) < 2:
            raise forms.ValidationError(_("Вкажіть імʼя (мінімум 2 символи)"))
        if len(name) > 255:
            raise forms.ValidationError(_("Імʼя занадто довге"))
        if not _NAME_RE.fullmatch(name):
            raise forms.ValidationError(
                _("Імʼя може містити лише літери, пробіли, дефіс і апостроф")
            )
        if not any(ch.isalpha() for ch in name):
            raise forms.ValidationError(_("Вкажіть коректне імʼя"))
        return name

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").lower().strip()
        if not email or not _EMAIL_RE.fullmatch(email):
            raise forms.ValidationError(_("Введіть коректну email-адресу"))
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(_("Користувач з таким email вже існує"))
        return email

    def clean_password1(self):
        password = self.cleaned_data.get("password1") or ""
        if len(password) < 8:
            raise forms.ValidationError(_("Пароль має містити щонайменше 8 символів"))
        if password.isdigit():
            raise forms.ValidationError(_("Пароль не може складатися лише з цифр"))
        if password.lower() == (self.data.get("email") or "").lower().strip():
            raise forms.ValidationError(_("Пароль не повинен збігатися з email"))
        return password

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
    email = forms.EmailField(label=_("Email"), required=True)

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
            "phone": forms.TextInput(attrs=PHONE_ATTRS),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        self.fields["email"].initial = self.user.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        email = self.cleaned_data["email"].lower().strip()
        self.user.email = email
        self.user.username = email
        if commit:
            self.user.save(update_fields=["email", "username"])
            profile.save()
        return profile
