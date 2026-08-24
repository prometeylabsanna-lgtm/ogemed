# Generated manually for one-SKU-per-product commerce fields on Product.

from decimal import Decimal

import django.db.models.deletion
from django.db import migrations, models


def copy_variant_commerce_to_product(apps, schema_editor):
    Product = apps.get_model("catalog", "Product")
    ProductVariant = apps.get_model("catalog", "ProductVariant")
    used_skus: set[str] = set()

    for product in Product.objects.all().iterator():
        variant = (
            ProductVariant.objects.filter(product_id=product.pk)
            .order_by("sort_order", "pk")
            .first()
        )
        if variant:
            sku = (variant.sku or "").strip() or f"SKU-{product.pk}"
            barcode = variant.barcode or ""
            price = variant.price if variant.price is not None else Decimal("0")
            old_price = variant.old_price
            wholesale_price = variant.wholesale_price
            stock = variant.stock or 0
        else:
            sku = f"SKU-{product.pk}"
            barcode = ""
            price = Decimal("0")
            old_price = None
            wholesale_price = None
            stock = 0

        base = sku
        n = 1
        while sku in used_skus:
            sku = f"{base}-{n}"
            n += 1
        used_skus.add(sku)

        Product.objects.filter(pk=product.pk).update(
            sku=sku,
            barcode=barcode,
            price=price,
            old_price=old_price,
            wholesale_price=wholesale_price,
            stock=stock,
        )

        if variant:
            ProductVariant.objects.filter(pk=variant.pk).update(
                sku=sku,
                is_active=True,
                sort_order=0,
            )
            ProductVariant.objects.filter(product_id=product.pk).exclude(
                pk=variant.pk
            ).update(is_active=False)


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0013_optimized_image_field"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="sku",
            field=models.CharField(
                blank=True, default="", max_length=64, verbose_name="Артикул (SKU)"
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="barcode",
            field=models.CharField(
                blank=True, default="", max_length=64, verbose_name="Штрихкод"
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="price",
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal("0"),
                max_digits=10,
                verbose_name="Ціна",
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="old_price",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                max_digits=10,
                null=True,
                verbose_name="Стара ціна",
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="wholesale_price",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                max_digits=10,
                null=True,
                verbose_name="Оптова ціна",
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="stock",
            field=models.PositiveIntegerField(default=0, verbose_name="Залишок"),
        ),
        migrations.RunPython(copy_variant_commerce_to_product, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="product",
            name="sku",
            field=models.CharField(
                max_length=64, unique=True, verbose_name="Артикул (SKU)"
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="barcode",
            field=models.CharField(
                blank=True, max_length=64, verbose_name="Штрихкод"
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="price",
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal("0"),
                max_digits=10,
                verbose_name="Ціна",
            ),
        ),
        migrations.AlterField(
            model_name="category",
            name="show_on_home",
            field=models.BooleanField(
                default=False,
                help_text=(
                    "Якщо увімкнено — категорія зʼявиться в блоці «Категорії» "
                    "на головній сторінці сайту (під hero)."
                ),
                verbose_name="Показувати в швидких категоріях на головній",
            ),
        ),
    ]
