from django.db import migrations, models

DEFAULT_TIKTOK_URL = "https://www.tiktok.com/@olga_cosm3"


def set_tiktok_url(apps, schema_editor):
    SiteSettings = apps.get_model("core", "SiteSettings")
    SiteSettings.objects.filter(pk=1).update(tiktok_url=DEFAULT_TIKTOK_URL)


def unset_tiktok_url(apps, schema_editor):
    SiteSettings = apps.get_model("core", "SiteSettings")
    SiteSettings.objects.filter(pk=1).update(tiktok_url="")


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0011_sitesettings_phone_2"),
    ]

    operations = [
        migrations.AddField(
            model_name="sitesettings",
            name="tiktok_url",
            field=models.URLField(blank=True, verbose_name="TikTok"),
        ),
        migrations.RunPython(set_tiktok_url, unset_tiktok_url),
    ]
