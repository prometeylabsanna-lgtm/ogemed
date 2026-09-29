"""Відновити повний текст юридичних сторінок: intro + секції → один body."""

from django.db import migrations

PAGE_KEYS = ("shipping", "returns", "privacy", "offer")


def _wrap_intro(intro: str) -> str:
    intro = (intro or "").strip()
    if not intro:
        return ""
    if "<" in intro and ">" in intro:
        return intro
    return f"<p>{intro}</p>"


def _combine(intro: str, merged: str) -> str:
    merged = (merged or "").strip()
    intro_html = _wrap_intro(intro)
    if not merged:
        return intro_html
    if not intro_html:
        return merged
    # Уже злито раніше — не дублюємо
    probe = intro_html.replace("<p>", "").replace("</p>", "").strip()[:40]
    if probe and probe in merged:
        return merged
    if "<h2>" in (intro or "") and intro_html.strip() == merged.strip():
        return merged
    # Якщо в body уже є заголовки секцій — лишаємо як є
    if "<h2>" in (intro or "") and merged[:50] in intro:
        return intro_html
    return f"{intro_html.rstrip()}\n{merged}"


def forwards(apps, schema_editor):
    from apps.cms.info_page_service import merge_sections_html_for_page

    CMSPage = apps.get_model("cms", "CMSPage")
    InfoPageSection = apps.get_model("cms", "InfoPageSection")

    for key in PAGE_KEYS:
        page = CMSPage.objects.filter(page_key=key).first()
        if page is None:
            continue

        # Усі секції (і активні, і вимкнені після 0016)
        merged_uk = merge_sections_html_for_page(
            key, lang="uk", include_inactive=True
        )
        merged_ru = merge_sections_html_for_page(
            key, lang="ru", include_inactive=True
        )
        if not merged_uk and not merged_ru:
            continue

        new_uk = _combine(page.body_uk or "", merged_uk)
        new_ru = _combine(page.body_ru or "", merged_ru)

        update_fields = []
        if new_uk != (page.body_uk or ""):
            page.body_uk = new_uk
            update_fields.append("body_uk")
        if new_ru != (page.body_ru or ""):
            page.body_ru = new_ru
            update_fields.append("body_ru")
        if update_fields:
            page.save(update_fields=update_fields)

        InfoPageSection.objects.filter(page_key=key).update(is_active=False)


def backwards(apps, schema_editor):
    # Не розбираємо HTML назад у секції
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("cms", "0016_merge_info_sections_into_body"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
