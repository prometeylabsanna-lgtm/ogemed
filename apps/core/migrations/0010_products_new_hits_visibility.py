# Generated manually — split home products visibility into new/hits.

from django.db import migrations


def forwards(apps, schema_editor):
    SiteBlock = apps.get_model("core", "SiteBlock")
    legacy = SiteBlock.objects.filter(page="home", key="products_section_visible").first()
    legacy_uk = "1"
    legacy_ru = "1"
    if legacy is not None:
        legacy_uk = (getattr(legacy, "text_html_uk", None) or legacy.text_html or "1").strip() or "1"
        legacy_ru = (getattr(legacy, "text_html_ru", None) or legacy_uk).strip() or legacy_uk

    for key, label in (
        ("products_new_visible", "Показувати блок «Новинки» на сайті"),
        ("products_hits_visible", "Показувати блок «Хіти» на сайті"),
    ):
        block, created = SiteBlock.objects.get_or_create(
            page="home",
            key=key,
            defaults={
                "label": label,
                "content_type": "text",
                "text_html": legacy_uk,
                "sort_order": 0,
                "is_active": True,
            },
        )
        if created:
            if hasattr(block, "text_html_uk"):
                block.text_html_uk = legacy_uk
                block.text_html_ru = legacy_ru
            block.text_html = legacy_uk
            block.save()


def backwards(apps, schema_editor):
    SiteBlock = apps.get_model("core", "SiteBlock")
    SiteBlock.objects.filter(
        page="home",
        key__in=["products_new_visible", "products_hits_visible"],
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0009_admin_uk_verbose_names"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
