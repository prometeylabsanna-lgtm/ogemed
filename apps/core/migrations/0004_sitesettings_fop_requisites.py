from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0003_site_settings_address_hours_map"),
    ]

    operations = [
        migrations.AddField(
            model_name="sitesettings",
            name="fop_card_number",
            field=models.CharField(
                blank=True, max_length=32, verbose_name="ФОП: номер картки"
            ),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="fop_edrpou",
            field=models.CharField(
                blank=True, max_length=20, verbose_name="ФОП: ЄДРПОУ / ІПН"
            ),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="fop_iban",
            field=models.CharField(blank=True, max_length=34, verbose_name="ФОП: IBAN"),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="fop_recipient_name",
            field=models.CharField(
                blank=True,
                help_text="ПІБ ФОП або назва для оплати за реквізитами",
                max_length=255,
                verbose_name="ФОП: одержувач",
            ),
        ),
    ]
