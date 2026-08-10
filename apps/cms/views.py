from django.views.generic import DetailView
from django.utils.translation import get_language

from apps.core.breadcrumbs import build_breadcrumbs

from . import info_page_content as info_content
from . import info_page_content_2 as info_content_legal
from .about_content import AboutContent
from .models import CMSPage


_INFO_TEMPLATES = {
    "about": "cms/about.html",
    "contacts": "cms/contacts.html",
    "shipping": "cms/shipping.html",
    "returns": "cms/returns.html",
    "privacy": "cms/privacy.html",
    "offer": "cms/offer.html",
}

_SLUG_TEMPLATES = {
    "pro-nas": "cms/about.html",
    "kontakty": "cms/contacts.html",
    "dostavka-i-oplata": "cms/shipping.html",
    "povernennya": "cms/returns.html",
    "polityka-konfidentsiynosti": "cms/privacy.html",
    "publichna-oferta": "cms/offer.html",
}


class CMSPageDetailView(DetailView):
    model = CMSPage
    template_name = "cms/page.html"
    context_object_name = "page"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return CMSPage.objects.filter(is_published=True)

    def get_template_names(self):
        page = self.object
        if page.page_key in _INFO_TEMPLATES:
            return [_INFO_TEMPLATES[page.page_key]]
        if page.slug in _SLUG_TEMPLATES:
            return [_SLUG_TEMPLATES[page.slug]]
        return super().get_template_names()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        page = self.object
        ctx["page_title"] = page.title
        body = (page.body or "").strip()
        if body:
            plain = " ".join(body.split())
            ctx["meta_description"] = plain[:160]
        else:
            ctx["meta_description"] = page.title
        ctx["breadcrumbs"] = build_breadcrumbs(
            self.request,
            (page.title, None),
        )
        if page.page_key == "about" or page.slug == "pro-nas":
            ctx["about"] = AboutContent.load()
        self._add_info_page_context(ctx, page)
        return ctx

    def _add_info_page_context(self, ctx: dict, page: CMSPage) -> None:
        key = page.page_key or ""
        slug = page.slug
        is_ru = (get_language() or "uk")[:2] == "ru"

        if key == "shipping" or slug == "dostavka-i-oplata":
            ctx["info_sections"] = info_content.shipping_sections()
            ctx["info_note"] = info_content.shipping_note()
            ctx["cta_title"] = (
                "Нужна помощь с заказом?" if is_ru else "Потрібна допомога із замовленням?"
            )
            ctx["cta_text"] = (
                "Уточним доставку Новой Почтой, оплату LiqPay или статус ТТН."
                if is_ru
                else "Уточнимо доставку Новою Поштою, оплату LiqPay або статус ТТН."
            )
        elif key == "returns" or slug == "povernennya":
            ctx["info_sections"] = info_content.returns_sections()
            ctx["cta_title"] = (
                "Есть вопрос по возврату?" if is_ru else "Є питання щодо повернення?"
            )
            ctx["cta_text"] = (
                "Напишите номер заказа — разберём брак, ошибку комплектации "
                "или повреждение в пути."
                if is_ru
                else "Напишіть номер замовлення — розберемо брак, помилку "
                "комплектації чи пошкодження в дорозі."
            )
        elif key == "privacy" or slug == "polityka-konfidentsiynosti":
            ctx["info_sections"] = info_content_legal.privacy_sections()
            ctx["cta_title"] = (
                "Вопросы по данным?" if is_ru else "Питання щодо даних?"
            )
            ctx["cta_text"] = (
                "Напишите на hello@ogemed.ua или оставьте заявку — ответим "
                "в рабочие часы."
                if is_ru
                else "Напишіть на hello@ogemed.ua або залиште заявку — відповімо "
                "у робочі години."
            )
        elif key == "offer" or slug == "publichna-oferta":
            ctx["info_sections"] = info_content_legal.offer_sections()
            ctx["cta_title"] = (
                "Нужны уточнения?" if is_ru else "Потрібні уточнення?"
            )
            ctx["cta_text"] = (
                "По условиям договора, доставке или оплате — менеджер на связи."
                if is_ru
                else "Щодо умов договору, доставки чи оплати — менеджер на звʼязку."
            )
