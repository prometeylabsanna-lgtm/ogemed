from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name=_("Користувач"),
    )
    full_name = models.CharField(_("ПІБ"), max_length=255, blank=True)
    phone = models.CharField(_("Телефон"), max_length=32, blank=True)
    default_city = models.CharField(_("Місто"), max_length=120, blank=True)
    default_street = models.CharField(_("Вулиця"), max_length=255, blank=True)
    default_building = models.CharField(_("Будинок"), max_length=64, blank=True)
    default_apartment = models.CharField(_("Квартира"), max_length=64, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Профіль")
        verbose_name_plural = _("Профілі")

    def __str__(self) -> str:
        return self.full_name or self.user.get_username()
