# Generated manually for legal page proxy models

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("cms", "0014_admin_hints_cta_labels"),
    ]

    operations = [
        migrations.CreateModel(
            name="LegalAboutPage",
            fields=[],
            options={
                "verbose_name": "Про нас",
                "verbose_name_plural": "Про нас",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("cms.cmspage",),
        ),
        migrations.CreateModel(
            name="LegalContactsPage",
            fields=[],
            options={
                "verbose_name": "Контакти",
                "verbose_name_plural": "Контакти",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("cms.cmspage",),
        ),
        migrations.CreateModel(
            name="LegalShippingPage",
            fields=[],
            options={
                "verbose_name": "Доставка і оплата",
                "verbose_name_plural": "Доставка і оплата",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("cms.cmspage",),
        ),
        migrations.CreateModel(
            name="LegalReturnsPage",
            fields=[],
            options={
                "verbose_name": "Повернення",
                "verbose_name_plural": "Повернення",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("cms.cmspage",),
        ),
        migrations.CreateModel(
            name="LegalPrivacyPage",
            fields=[],
            options={
                "verbose_name": "Конфіденційність",
                "verbose_name_plural": "Конфіденційність",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("cms.cmspage",),
        ),
        migrations.CreateModel(
            name="LegalOfferPage",
            fields=[],
            options={
                "verbose_name": "Оферта",
                "verbose_name_plural": "Оферта",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("cms.cmspage",),
        ),
    ]
