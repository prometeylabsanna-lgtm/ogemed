from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="payment_type",
            field=models.CharField(
                choices=[
                    ("liqpay", "LiqPay"),
                    ("cash_on_delivery", "Оплата при отриманні"),
                    ("fop_card", "Оплата на картку / рахунок ФОП"),
                ],
                max_length=32,
                verbose_name="Оплата",
            ),
        ),
    ]
