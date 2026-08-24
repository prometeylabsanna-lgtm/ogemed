"""Спільні правила валідації полів форм (імʼя, телефон, email, повідомлення)."""

from __future__ import annotations

import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

NAME_MIN = 2
NAME_MAX = 50
MESSAGE_MIN = 15
MESSAGE_MAX = 2000
PASSWORD_MIN = 8

_NAME_RE = re.compile(
    r"^[A-Za-zА-Яа-яЁёІіЇїЄєҐґʼ'`’\- ]+$",
    re.UNICODE,
)
_URLISH_RE = re.compile(r"(https?://|www\.|[a-z0-9-]+\.[a-z]{2,})", re.IGNORECASE)
_EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]{2,}$")
_HTML_TAG_RE = re.compile(r"<[^>]*>")
_PHONE_DIGITS_RE = re.compile(r"\D+")


def normalize_name(value: str | None) -> str:
    name = (value or "").strip()
    return re.sub(r"\s+", " ", name)


def validate_name(value: str | None, *, required: bool = True) -> str:
    name = normalize_name(value)
    if not name:
        if required:
            raise ValidationError(_("Будь ласка, вкажіть ваше імʼя."))
        return ""
    if len(name) < NAME_MIN:
        raise ValidationError(
            _("Імʼя надто коротке. Введіть щонайменше 2 літери.")
        )
    if len(name) > NAME_MAX:
        raise ValidationError(
            _("Імʼя занадто довге (максимум %(max)s символів).")
            % {"max": NAME_MAX}
        )
    if (
        _URLISH_RE.search(name)
        or not _NAME_RE.fullmatch(name)
        or not any(ch.isalpha() for ch in name)
    ):
        raise ValidationError(
            _(
                "Імʼя не може містити цифри та спецсимволи. "
                "Використовуйте лише літери."
            )
        )
    return name


def normalize_phone(value: str | None) -> str:
    digits = _PHONE_DIGITS_RE.sub("", value or "")
    if digits.startswith("0") and len(digits) == 10:
        digits = "380" + digits[1:]
    return digits


def validate_phone(value: str | None, *, required: bool = True) -> str:
    raw = (value or "").strip()
    if not raw:
        if required:
            raise ValidationError(_("Введіть номер телефону."))
        return ""
    digits = normalize_phone(raw)
    if not digits or digits == "380":
        if required:
            raise ValidationError(_("Введіть номер телефону."))
        return ""
    if digits.startswith("380") and len(digits) < 12:
        raise ValidationError(
            _(
                "Введіть повний номер телефону: +380 XX XXX XX XX "
                "(не вистачає цифр)."
            )
        )
    if not re.fullmatch(r"380\d{9}", digits):
        raise ValidationError(
            _(
                "Невірний формат номера. Перевірте правильність введених цифр."
            )
        )
    return "+" + digits


def normalize_email(value: str | None) -> str:
    return (value or "").strip().lower()


def validate_email(value: str | None, *, required: bool = True) -> str:
    email = normalize_email(value)
    if not email:
        if required:
            raise ValidationError(
                _("Електронна пошта обовʼязкова для заповнення.")
            )
        return ""
    if not _EMAIL_RE.fullmatch(email):
        raise ValidationError(
            _(
                "Введіть коректну email-адресу (наприклад: name@domain.com)."
            )
        )
    return email


def sanitize_message(value: str | None) -> str:
    text = _HTML_TAG_RE.sub("", value or "")
    text = text.replace("\x00", "").strip()
    return text


def validate_message(value: str | None, *, required: bool = False) -> str:
    text = sanitize_message(value)
    if not text:
        if required:
            raise ValidationError(_("Напишіть текст вашого повідомлення."))
        return ""
    if len(text) < MESSAGE_MIN:
        left = MESSAGE_MIN - len(text)
        raise ValidationError(
            _(
                "Повідомлення занадто коротке. Опишіть детальніше "
                "(мінімум 15 символів). Залишилось ввести ще %(left)s симв."
            )
            % {"left": left}
        )
    if len(text) > MESSAGE_MAX:
        raise ValidationError(
            _("Перевищено максимальний ліміт у 2000 символів.")
        )
    return text


def validate_password_register(value: str | None, *, email: str = "") -> str:
    password = value or ""
    if not password:
        raise ValidationError(_("Обовʼязкове поле"))
    if len(password) < PASSWORD_MIN:
        raise ValidationError(
            _("Пароль має містити щонайменше %(min)s символів")
            % {"min": PASSWORD_MIN}
        )
    if password.isdigit():
        raise ValidationError(_("Пароль не може складатися лише з цифр"))
    if email and password.lower() == email.lower().strip():
        raise ValidationError(_("Пароль не повинен збігатися з email"))
    return password
