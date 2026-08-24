"""Завантаження секцій інфо-сторінок з БД (з fallback на hardcoded)."""
from __future__ import annotations

from django.utils.html import linebreaks

from apps.cms import info_page_content as hardcoded
from apps.cms import info_page_content_2 as hardcoded_legal
from apps.cms.info_page_models import InfoPageMeta, InfoPageSection


def _plain_to_html(text: str) -> str:
    text = (text or "").strip()
    if not text:
        return ""
    if "<" in text and ">" in text:
        return text
    return linebreaks(text)


def sections_for_page(page_key: str) -> list[dict]:
    qs = InfoPageSection.objects.filter(page_key=page_key, is_active=True)
    rows = list(qs)
    if rows:
        out: list[dict] = []
        for row in rows:
            if row.layout == InfoPageSection.Layout.PROSE:
                out.append(
                    {
                        "title": row.heading,
                        "body": row.body,
                        "layout": "prose",
                    }
                )
            else:
                out.append(
                    {
                        "label": row.heading,
                        "value": row.subheading,
                        "text": row.body,
                        "layout": "card",
                    }
                )
        return out

    if page_key == "shipping":
        return [
            {
                "label": item["label"],
                "value": item["value"],
                "text": _plain_to_html(item["text"]),
                "layout": "card",
            }
            for item in hardcoded.shipping_sections()
        ]
    if page_key == "returns":
        return [
            {
                "label": item["label"],
                "value": item["value"],
                "text": _plain_to_html(item["text"]),
                "layout": "card",
            }
            for item in hardcoded.returns_sections()
        ]
    if page_key == "privacy":
        return [
            {
                "title": item["title"],
                "body": _plain_to_html(item["body"]),
                "layout": "prose",
            }
            for item in hardcoded_legal.privacy_sections()
        ]
    if page_key == "offer":
        return [
            {
                "title": item["title"],
                "body": _plain_to_html(item["body"]),
                "layout": "prose",
            }
            for item in hardcoded_legal.offer_sections()
        ]
    return []


def meta_for_page(page_key: str) -> dict:
    meta = InfoPageMeta.objects.filter(page_key=page_key).first()
    if meta:
        note = None
        steps = meta.note_steps()
        note_text = meta.note_text
        if meta.note_title or steps or note_text:
            note = {
                "title": meta.note_title,
                "steps": steps,
                "text": note_text,
            }
        return {
            "cta_title": meta.cta_title,
            "cta_text": meta.cta_text,
            "info_note": note,
        }

    from django.utils.translation import get_language

    is_ru = (get_language() or "uk")[:2] == "ru"

    if page_key == "shipping":
        return {
            "cta_title": (
                "Нужна помощь с заказом?" if is_ru else "Потрібна допомога із замовленням?"
            ),
            "cta_text": (
                "Уточним доставку Новой Почтой, оплату LiqPay или статус ТТН."
                if is_ru
                else "Уточнимо доставку Новою Поштою, оплату LiqPay або статус ТТН."
            ),
            "info_note": hardcoded.shipping_note(),
        }
    if page_key == "returns":
        return {
            "cta_title": (
                "Есть вопрос по возврату?" if is_ru else "Є питання щодо повернення?"
            ),
            "cta_text": (
                "Напишите номер заказа — разберём брак, ошибку комплектации "
                "или повреждение в пути."
                if is_ru
                else "Напишіть номер замовлення — розберемо брак, помилку "
                "комплектації чи пошкодження в дорозі."
            ),
            "info_note": None,
        }
    if page_key == "privacy":
        return {
            "cta_title": "Вопросы по данным?" if is_ru else "Питання щодо даних?",
            "cta_text": (
                "Напишите на hello@ogemed.ua или оставьте заявку — ответим "
                "в рабочие часы."
                if is_ru
                else "Напишіть на hello@ogemed.ua або залиште заявку — відповімо "
                "у робочі години."
            ),
            "info_note": None,
        }
    if page_key == "offer":
        return {
            "cta_title": "Нужны уточнения?" if is_ru else "Потрібні уточнення?",
            "cta_text": (
                "По условиям договора, доставке или оплате — менеджер на связи."
                if is_ru
                else "Щодо умов договору, доставки чи оплати — менеджер на звʼязку."
            ),
            "info_note": None,
        }
    return {"cta_title": "", "cta_text": "", "info_note": None}


def seed_payloads() -> list[dict]:
    """Дані для ідемпотентного seed (uk/ru окремо)."""
    from django.utils.translation import activate, deactivate

    payloads: list[dict] = []

    def _card_sections(page_key: str, getter):
        activate("uk")
        uk_items = getter()
        activate("ru")
        ru_items = getter()
        deactivate()
        for i, (uk, ru) in enumerate(zip(uk_items, ru_items)):
            payloads.append(
                {
                    "page_key": page_key,
                    "layout": InfoPageSection.Layout.CARD,
                    "sort_order": i,
                    "heading_uk": uk["label"],
                    "heading_ru": ru["label"],
                    "subheading_uk": uk.get("value", ""),
                    "subheading_ru": ru.get("value", ""),
                    "body_uk": _plain_to_html(uk.get("text", "")),
                    "body_ru": _plain_to_html(ru.get("text", "")),
                }
            )

    def _prose_sections(page_key: str, getter):
        activate("uk")
        uk_items = getter()
        activate("ru")
        ru_items = getter()
        deactivate()
        for i, (uk, ru) in enumerate(zip(uk_items, ru_items)):
            payloads.append(
                {
                    "page_key": page_key,
                    "layout": InfoPageSection.Layout.PROSE,
                    "sort_order": i,
                    "heading_uk": uk["title"],
                    "heading_ru": ru["title"],
                    "subheading_uk": "",
                    "subheading_ru": "",
                    "body_uk": _plain_to_html(uk.get("body", "")),
                    "body_ru": _plain_to_html(ru.get("body", "")),
                }
            )

    _card_sections("shipping", hardcoded.shipping_sections)
    _card_sections("returns", hardcoded.returns_sections)
    _prose_sections("privacy", hardcoded_legal.privacy_sections)
    _prose_sections("offer", hardcoded_legal.offer_sections)
    return payloads


def seed_meta_payloads() -> list[dict]:
    from django.utils.translation import activate, deactivate

    activate("uk")
    ship_note_uk = hardcoded.shipping_note()
    activate("ru")
    ship_note_ru = hardcoded.shipping_note()
    deactivate()

    def steps_text(note: dict) -> str:
        return "\n".join(s["text"] for s in note.get("steps") or [])

    return [
        {
            "page_key": "shipping",
            "cta_title_uk": "Потрібна допомога із замовленням?",
            "cta_title_ru": "Нужна помощь с заказом?",
            "cta_text_uk": (
                "Уточнимо доставку Новою Поштою, оплату LiqPay або статус ТТН."
            ),
            "cta_text_ru": (
                "Уточним доставку Новой Почтой, оплату LiqPay или статус ТТН."
            ),
            "note_title_uk": ship_note_uk["title"],
            "note_title_ru": ship_note_ru["title"],
            "note_steps_uk": steps_text(ship_note_uk),
            "note_steps_ru": steps_text(ship_note_ru),
            "note_text_uk": "",
            "note_text_ru": "",
        },
        {
            "page_key": "returns",
            "cta_title_uk": "Є питання щодо повернення?",
            "cta_title_ru": "Есть вопрос по возврату?",
            "cta_text_uk": (
                "Напишіть номер замовлення — розберемо брак, помилку "
                "комплектації чи пошкодження в дорозі."
            ),
            "cta_text_ru": (
                "Напишите номер заказа — разберём брак, ошибку комплектации "
                "или повреждение в пути."
            ),
        },
        {
            "page_key": "privacy",
            "cta_title_uk": "Питання щодо даних?",
            "cta_title_ru": "Вопросы по данным?",
            "cta_text_uk": (
                "Напишіть на hello@ogemed.ua або залиште заявку — відповімо "
                "у робочі години."
            ),
            "cta_text_ru": (
                "Напишите на hello@ogemed.ua или оставьте заявку — ответим "
                "в рабочие часы."
            ),
        },
        {
            "page_key": "offer",
            "cta_title_uk": "Потрібні уточнення?",
            "cta_title_ru": "Нужны уточнения?",
            "cta_text_uk": (
                "Щодо умов договору, доставки чи оплати — менеджер на звʼязку."
            ),
            "cta_text_ru": (
                "По условиям договора, доставке или оплате — менеджер на связи."
            ),
        },
    ]
