from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("payments", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="paymentattempt",
            name="provider",
            field=models.CharField(
                default="monopay", max_length=32, verbose_name="Провайдер"
            ),
        ),
    ]
