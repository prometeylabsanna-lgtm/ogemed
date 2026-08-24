# Generated manually for LabelIcon title_uk / title_ru

from django.db import migrations, models


TITLE_RU = {
    "perfume_off": "Без ароматизаторов",
    "branch": "Веган-формула",
    "face_check": "Дерматологически протестировано",
    "leaf_soft": "Деликатная формула",
    "hand_drop": "Гипоаллергенно",
    "flask_off": "Без парабенов",
    "bunny_off": "Без тестов на животных",
    "face_care": "Очищение",
}


def fill_title_ru(apps, schema_editor):
    LabelIcon = apps.get_model("catalog", "LabelIcon")
    for obj in LabelIcon.objects.all():
        if not obj.title_ru:
            obj.title_ru = TITLE_RU.get(obj.key, "")
            obj.save(update_fields=["title_ru"])


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0015_admin_ux_seo_status_brand_cleanup"),
    ]

    operations = [
        migrations.RenameField(
            model_name="labelicon",
            old_name="title",
            new_name="title_uk",
        ),
        migrations.AlterField(
            model_name="labelicon",
            name="title_uk",
            field=models.CharField(max_length=120, verbose_name="Підпис (UK)"),
        ),
        migrations.AddField(
            model_name="labelicon",
            name="title_ru",
            field=models.CharField(
                blank=True, max_length=120, verbose_name="Підпис (RU)"
            ),
        ),
        migrations.AlterModelOptions(
            name="labelicon",
            options={
                "ordering": ["title_uk"],
                "verbose_name": "Іконка мітки",
                "verbose_name_plural": "Іконки міток",
            },
        ),
        migrations.RunPython(fill_title_ru, migrations.RunPython.noop),
    ]
