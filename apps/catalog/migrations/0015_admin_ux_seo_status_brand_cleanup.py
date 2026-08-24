# Generated manually for safe SEO field rename + status cleanup.

from django.db import migrations, models


def copy_seo_to_uk(apps, schema_editor):
    for model_name in ("Brand", "Category", "Product"):
        Model = apps.get_model("catalog", model_name)
        for obj in Model.objects.all().only(
            "pk", "seo_title", "seo_description"
        ):
            Model.objects.filter(pk=obj.pk).update(
                seo_title_uk=obj.seo_title or "",
                seo_description_uk=obj.seo_description or "",
            )


def migrate_product_status(apps, schema_editor):
    Product = apps.get_model("catalog", "Product")
    Product.objects.filter(status__in=("draft", "archived")).update(
        status="inactive",
        is_active=False,
    )
    Product.objects.filter(status="active").update(is_active=True)


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0014_product_commerce_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="brand",
            name="seo_description_ru",
            field=models.TextField(blank=True, verbose_name="SEO description (RU)"),
        ),
        migrations.AddField(
            model_name="brand",
            name="seo_description_uk",
            field=models.TextField(blank=True, verbose_name="SEO description (UK)"),
        ),
        migrations.AddField(
            model_name="brand",
            name="seo_title_ru",
            field=models.CharField(
                blank=True, max_length=255, verbose_name="SEO title (RU)"
            ),
        ),
        migrations.AddField(
            model_name="brand",
            name="seo_title_uk",
            field=models.CharField(
                blank=True, max_length=255, verbose_name="SEO title (UK)"
            ),
        ),
        migrations.AddField(
            model_name="category",
            name="seo_description_ru",
            field=models.TextField(blank=True, verbose_name="SEO description (RU)"),
        ),
        migrations.AddField(
            model_name="category",
            name="seo_description_uk",
            field=models.TextField(blank=True, verbose_name="SEO description (UK)"),
        ),
        migrations.AddField(
            model_name="category",
            name="seo_title_ru",
            field=models.CharField(
                blank=True, max_length=255, verbose_name="SEO title (RU)"
            ),
        ),
        migrations.AddField(
            model_name="category",
            name="seo_title_uk",
            field=models.CharField(
                blank=True, max_length=255, verbose_name="SEO title (UK)"
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="seo_description_ru",
            field=models.TextField(blank=True, verbose_name="SEO description (RU)"),
        ),
        migrations.AddField(
            model_name="product",
            name="seo_description_uk",
            field=models.TextField(blank=True, verbose_name="SEO description (UK)"),
        ),
        migrations.AddField(
            model_name="product",
            name="seo_title_ru",
            field=models.CharField(
                blank=True, max_length=255, verbose_name="SEO title (RU)"
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="seo_title_uk",
            field=models.CharField(
                blank=True, max_length=255, verbose_name="SEO title (UK)"
            ),
        ),
        migrations.RunPython(copy_seo_to_uk, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="brand",
            name="seo_description",
        ),
        migrations.RemoveField(
            model_name="brand",
            name="seo_title",
        ),
        migrations.RemoveField(
            model_name="category",
            name="seo_description",
        ),
        migrations.RemoveField(
            model_name="category",
            name="seo_title",
        ),
        migrations.RemoveField(
            model_name="product",
            name="seo_description",
        ),
        migrations.RemoveField(
            model_name="product",
            name="seo_title",
        ),
        migrations.RemoveField(
            model_name="brand",
            name="categories",
        ),
        migrations.RemoveField(
            model_name="brand",
            name="logo",
        ),
        migrations.RemoveField(
            model_name="brand",
            name="logo_dark",
        ),
        migrations.RemoveField(
            model_name="brand",
            name="website_url",
        ),
        migrations.RunPython(migrate_product_status, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="product",
            name="status",
            field=models.CharField(
                choices=[("active", "Активний"), ("inactive", "Неактивний")],
                default="active",
                max_length=16,
                verbose_name="Статус",
            ),
        ),
        migrations.AlterField(
            model_name="productimage",
            name="alt_ru",
            field=models.CharField(
                blank=True, max_length=255, verbose_name="Назва (RU)"
            ),
        ),
        migrations.AlterField(
            model_name="productimage",
            name="alt_uk",
            field=models.CharField(
                blank=True, max_length=255, verbose_name="Назва (UK)"
            ),
        ),
    ]
