"""modeltranslation: SiteBlock.text_html → text_html_uk / text_html_ru."""
from modeltranslation.translator import TranslationOptions, register

from apps.core.models import SiteBlock


@register(SiteBlock)
class SiteBlockTranslationOptions(TranslationOptions):
    fields = ("text_html",)
