from django.db import migrations, models


class Migration(migrations.Migration):
    """Мітка «Глибоке зволоження» стала «Очищення».

    RenameField замість remove+add: вже проставлені значення чекбокса зберігаються.
    """

    dependencies = [
        ("catalog", "0005_delete_productclaim"),
    ]

    operations = [
        migrations.RenameField(
            model_name="product",
            old_name="label_hydration",
            new_name="label_cleansing",
        ),
        migrations.AlterField(
            model_name="product",
            name="label_cleansing",
            field=models.BooleanField(default=False, verbose_name="Очищення"),
        ),
    ]
