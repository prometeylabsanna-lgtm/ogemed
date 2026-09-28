from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0003_admin_uk_verbose_names"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="payment_type",
            field=models.CharField(
                choices=[
                    ("monopay", "Онлайн оплата (Monobank)"),
                    ("cash_on_delivery", "Оплата при отриманні"),
                    ("fop_card", "Оплата на картку / рахунок ФОП"),
                ],
                max_length=32,
                verbose_name="Оплата",
            ),
        ),
    ]
