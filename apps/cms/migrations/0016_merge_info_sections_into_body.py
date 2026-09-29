"""Злити InfoPageSection у CMSPage.body — один редактор на сторінку."""

from django.db import migrations


PAGE_KEYS = ("shipping", "returns", "privacy", "offer")

SLUG_BY_KEY = {
    "shipping": "dostavka-i-oplata",
    "returns": "povernennya",
    "privacy": "polityka-konfidentsiynosti",
    "offer": "publichna-oferta",
}

TITLE_BY_KEY = {
    "shipping": ("Доставка і оплата", "Доставка и оплата"),
    "returns": ("Повернення", "Возврат"),
    "privacy": ("Політика конфіденційності", "Политика конфиденциальности"),
    "offer": ("Публічна оферта", "Публичная оферта"),
}


def _is_blank_html(value: str) -> bool:
    text = (value or "").strip()
    if not text:
        return True
    stripped = (
        text.replace("&nbsp;", " ")
        .replace("<p>", "")
        .replace("</p>", "")
        .replace("<br>", "")
        .replace("<br/>", "")
        .replace("<br />", "")
        .strip()
    )
    return not stripped


def forwards(apps, schema_editor):
    from apps.cms.info_page_service import merge_sections_html_for_page

    CMSPage = apps.get_model("cms", "CMSPage")
    InfoPageSection = apps.get_model("cms", "InfoPageSection")

    for key in PAGE_KEYS:
        page = CMSPage.objects.filter(page_key=key).first()
        if page is None:
            page = CMSPage.objects.filter(slug=SLUG_BY_KEY[key]).first()
        if page is None:
            title_uk, title_ru = TITLE_BY_KEY[key]
            page = CMSPage.objects.create(
                slug=SLUG_BY_KEY[key],
                page_key=key,
                title_uk=title_uk,
                title_ru=title_ru,
                body_uk="",
                body_ru="",
                is_published=True,
            )
        elif not page.page_key:
            page.page_key = key
            page.save(update_fields=["page_key"])

        merged_uk = merge_sections_html_for_page(key, lang="uk")
        merged_ru = merge_sections_html_for_page(key, lang="ru")

        update_fields: list[str] = []
        # Не чіпаємо body, якщо адмін уже заповнив текст — лише доливаємо, коли порожньо.
        # (Повне відновлення intro+секції — у 0017.)
        if merged_uk and _is_blank_html(page.body_uk):
            page.body_uk = merged_uk
            update_fields.append("body_uk")
        if merged_ru and _is_blank_html(page.body_ru):
            page.body_ru = merged_ru
            update_fields.append("body_ru")

        if update_fields:
            page.save(update_fields=update_fields)

        # Не вимикаємо секції тут — 0017 зливає й вимикає після відновлення.


def backwards(apps, schema_editor):
    InfoPageSection = apps.get_model("cms", "InfoPageSection")
    InfoPageSection.objects.filter(page_key__in=PAGE_KEYS).update(is_active=True)


class Migration(migrations.Migration):
    dependencies = [
        ("cms", "0015_legal_page_proxies"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
