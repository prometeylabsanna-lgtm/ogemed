from django.db import models
from django.utils.translation import get_language, gettext_lazy as _

from apps.core.fields import OptimizedImageField
from apps.core.image_processing import MAX_SIDE_HERO, MAX_SIDE_PRODUCT


class AboutContent(models.Model):
    """Singleton content for /pro-nas/ — секції з окремими полями UK/RU."""

    # —— Верхній банер ——
    hero_visible = models.BooleanField(_("Показувати верхній банер"), default=True)
    hero_kicker_uk = models.CharField(
        _("Надпис над заголовком [UA]"),
        max_length=80,
        blank=True,
        default="OGEMED for you",
    )
    hero_kicker_ru = models.CharField(
        _("Надпис над заголовком [RU]"),
        max_length=80,
        blank=True,
        default="OGEMED for you",
    )
    hero_title_uk = models.CharField(
        _("Заголовок банера [UA]"),
        max_length=160,
        blank=True,
        default="Краса з турботою про вас",
    )
    hero_title_ru = models.CharField(
        _("Заголовок банера [RU]"),
        max_length=160,
        blank=True,
        default="Красота с заботой о вас",
    )
    hero_text_uk = models.TextField(
        _("Текст банера [UA]"),
        blank=True,
        default=(
            "Ми допомагаємо обрати догляд, якому можна довіряти — "
            "спокійно, чесно і з увагою до вашої шкіри."
        ),
    )
    hero_text_ru = models.TextField(
        _("Текст банера [RU]"),
        blank=True,
        default=(
            "Мы помогаем выбрать уход, которому можно доверять — "
            "спокойно, честно и с вниманием к вашей коже."
        ),
    )
    hero_image = OptimizedImageField(
        _("Зображення банера"),
        upload_to="about/",
        blank=True,
        max_side=MAX_SIDE_HERO,
        help_text=_("Верхній банер «Про нас». Desktop ≈ 1920×800, WebP/JPEG."),
    )

    # —— Історія ——
    history_visible = models.BooleanField(_("Історія видима"), default=True)
    history_kicker_uk = models.CharField(
        _("Надпис секції «Історія» [UA]"),
        max_length=80,
        blank=True,
        default="Історія",
    )
    history_kicker_ru = models.CharField(
        _("Надпис секції «Історія» [RU]"),
        max_length=80,
        blank=True,
        default="История",
    )
    history_title_uk = models.CharField(
        _("Історія заголовок (UK)"),
        max_length=160,
        blank=True,
        default="Як зʼявився OGEMED for you",
    )
    history_title_ru = models.CharField(
        _("Історія заголовок (RU)"),
        max_length=160,
        blank=True,
        default="Как появился OGEMED for you",
    )
    history_body_uk = models.TextField(
        _("Історія текст (UK, запасний)"),
        blank=True,
        default="",
    )
    history_body_ru = models.TextField(
        _("Історія текст (RU, запасний)"),
        blank=True,
        default="",
    )
    history_image = OptimizedImageField(
        _("Історія зображення"),
        upload_to="about/",
        blank=True,
        max_side=MAX_SIDE_PRODUCT,
    )
    history_card_1_title_uk = models.CharField(
        _("Картка 1 — заголовок (UK)"),
        max_length=160,
        blank=True,
        default="Як зʼявився OGEMED for you",
    )
    history_card_1_title_ru = models.CharField(
        _("Картка 1 — заголовок (RU)"),
        max_length=160,
        blank=True,
        default="Как появился OGEMED for you",
    )
    history_card_1_body_uk = models.TextField(
        _("Картка 1 — текст (UK)"),
        blank=True,
        default=(
            "OGEMED for you народився з простого бажання — зробити вибір "
            "косметики зрозумілим і спокійним. Замість хаосу обіцянок ми "
            "хотіли зібрати простір, де можна спокійно обрати догляд.\n\n"
            "Спочатку це були рекомендації друзям і близьким. Згодом — "
            "каталог брендів, яким ми довіряємо самі, і сервіс з увагою "
            "до деталей: від складу до умов зберігання."
        ),
    )
    history_card_1_body_ru = models.TextField(
        _("Картка 1 — текст (RU)"),
        blank=True,
        default=(
            "OGEMED for you родился из простого желания — сделать выбор "
            "косметики понятным и спокойным. Вместо хаоса обещаний мы "
            "хотели собрать пространство, где можно спокойно выбрать уход.\n\n"
            "Сначала это были рекомендации друзьям и близким. Затем — "
            "каталог брендов, которым мы доверяем сами, и сервис с вниманием "
            "к деталям: от состава до условий хранения."
        ),
    )
    history_card_2_title_uk = models.CharField(
        _("Картка 2 — заголовок (UK)"),
        max_length=160,
        blank=True,
        default="Що ми відбираємо для каталогу",
    )
    history_card_2_title_ru = models.CharField(
        _("Картка 2 — заголовок (RU)"),
        max_length=160,
        blank=True,
        default="Что мы отбираем для каталога",
    )
    history_card_2_body_uk = models.TextField(
        _("Картка 2 — текст (UK)"),
        blank=True,
        default=(
            "Ми дивимось не лише на «красиву банку». Важливі склад, "
            "репутація виробника, логістика й те, як засіб працює "
            "в щоденній рутині — без зайвого шуму й тиску.\n\n"
            "Кожен бренд у каталозі проходить внутрішній відбір: "
            "чи зрозумілі описи, чи чесні очікування, чи зручно "
            "пояснити клієнту, навіщо саме цей продукт."
        ),
    )
    history_card_2_body_ru = models.TextField(
        _("Картка 2 — текст (RU)"),
        blank=True,
        default=(
            "Мы смотрим не только на «красивую банку». Важны состав, "
            "репутация производителя, логистика и то, как средство "
            "работает в ежедневной рутине — без лишнего шума и давления.\n\n"
            "Каждый бренд в каталоге проходит внутренний отбор: "
            "понятны ли описания, честны ли ожидания, удобно ли "
            "объяснить клиенту, зачем именно этот продукт."
        ),
    )
    history_card_3_title_uk = models.CharField(
        _("Картка 3 — заголовок (UK)"),
        max_length=160,
        blank=True,
        default="Як супроводжуємо замовлення",
    )
    history_card_3_title_ru = models.CharField(
        _("Картка 3 — заголовок (RU)"),
        max_length=160,
        blank=True,
        default="Как сопровождаем заказ",
    )
    history_card_3_body_uk = models.TextField(
        _("Картка 3 — текст (UK)"),
        blank=True,
        default=(
            "Ми поруч на кожному кроці: допоможемо з підбором, "
            "підкажемо щодо доставки Новою Поштою чи курʼєром "
            "і відповімо після отримання, якщо щось треба уточнити.\n\n"
            "OGEMED for you — це не лише вітрина. Це турбота про те, "
            "щоб шлях від вибору до вашої полиці в Україні був "
            "спокійним, зрозумілим і без зайвих сюрпризів."
        ),
    )
    history_card_3_body_ru = models.TextField(
        _("Картка 3 — текст (RU)"),
        blank=True,
        default=(
            "Мы рядом на каждом шаге: поможем с подбором, "
            "подскажем по доставке Новой Почтой или курьером "
            "и ответим после получения, если что-то нужно уточнить.\n\n"
            "OGEMED for you — это не только витрина. Это забота о том, "
            "чтобы путь от выбора до вашей полки в Украине был "
            "спокойным, понятным и без лишних сюрпризов."
        ),
    )

    # —— Філософія ——
    philosophy_visible = models.BooleanField(_("Філософія видима"), default=True)
    philosophy_kicker_uk = models.CharField(
        _("Надпис секції «Філософія» [UA]"),
        max_length=80,
        blank=True,
        default="Філософія догляду",
    )
    philosophy_kicker_ru = models.CharField(
        _("Надпис секції «Філософія» [RU]"),
        max_length=80,
        blank=True,
        default="Философия ухода",
    )
    philosophy_title_uk = models.CharField(
        _("Філософія заголовок (UK)"),
        max_length=160,
        blank=True,
        default="Менше шуму — більше уваги до шкіри",
    )
    philosophy_title_ru = models.CharField(
        _("Філософія заголовок (RU)"),
        max_length=160,
        blank=True,
        default="Меньше шума — больше внимания к коже",
    )
    philosophy_body_uk = models.TextField(
        _("Філософія вступ (UK)"),
        blank=True,
        default="Три принципи, з яких ми збираємо каталог і сервіс.",
    )
    philosophy_body_ru = models.TextField(
        _("Філософія вступ (RU)"),
        blank=True,
        default="Три принципа, из которых мы собираем каталог и сервис.",
    )
    philosophy_image = OptimizedImageField(
        _("Філософія зображення"),
        upload_to="about/",
        blank=True,
        max_side=MAX_SIDE_PRODUCT,
    )
    philosophy_thesis_1_title_uk = models.CharField(
        _("Теза 1 — заголовок (UK)"),
        max_length=120,
        blank=True,
        default="Турбота",
    )
    philosophy_thesis_1_title_ru = models.CharField(
        _("Теза 1 — заголовок (RU)"),
        max_length=120,
        blank=True,
        default="Забота",
    )
    philosophy_thesis_1_text_uk = models.TextField(
        _("Теза 1 — текст (UK)"),
        blank=True,
        default="Мʼякий підхід до шкіри без зайвого тиску.",
    )
    philosophy_thesis_1_text_ru = models.TextField(
        _("Теза 1 — текст (RU)"),
        blank=True,
        default="Мягкий подход к коже без лишнего давления.",
    )
    philosophy_thesis_2_title_uk = models.CharField(
        _("Теза 2 — заголовок (UK)"),
        max_length=120,
        blank=True,
        default="Довіра",
    )
    philosophy_thesis_2_title_ru = models.CharField(
        _("Теза 2 — заголовок (RU)"),
        max_length=120,
        blank=True,
        default="Доверие",
    )
    philosophy_thesis_2_text_uk = models.TextField(
        _("Теза 2 — текст (UK)"),
        blank=True,
        default="Чесні склади й бренди, яким ми довіряємо самі.",
    )
    philosophy_thesis_2_text_ru = models.TextField(
        _("Теза 2 — текст (RU)"),
        blank=True,
        default="Честные составы и бренды, которым мы доверяем сами.",
    )
    philosophy_thesis_3_title_uk = models.CharField(
        _("Теза 3 — заголовок (UK)"),
        max_length=120,
        blank=True,
        default="Баланс",
    )
    philosophy_thesis_3_title_ru = models.CharField(
        _("Теза 3 — заголовок (RU)"),
        max_length=120,
        blank=True,
        default="Баланс",
    )
    philosophy_thesis_3_text_uk = models.TextField(
        _("Теза 3 — текст (UK)"),
        blank=True,
        default="Міра між ефективністю й мʼякістю — без крайнощів.",
    )
    philosophy_thesis_3_text_ru = models.TextField(
        _("Теза 3 — текст (RU)"),
        blank=True,
        default="Мера между эффективностью и мягкостью — без крайностей.",
    )
    philosophy_thesis_4_title_uk = models.CharField(
        _("Теза 4 — заголовок (UK)"),
        max_length=120,
        blank=True,
        default="Впевнений вибір",
    )
    philosophy_thesis_4_title_ru = models.CharField(
        _("Теза 4 — заголовок (RU)"),
        max_length=120,
        blank=True,
        default="Уверенный выбор",
    )
    philosophy_thesis_4_text_uk = models.TextField(
        _("Теза 4 — текст (UK)"),
        blank=True,
        default="Спокій у рішенні замість втоми від нескінченного шуму.",
    )
    philosophy_thesis_4_text_ru = models.TextField(
        _("Теза 4 — текст (RU)"),
        blank=True,
        default="Спокойствие в решении вместо усталости от бесконечного шума.",
    )

    # —— Нижній заклик ——
    cta_visible = models.BooleanField(_("Показувати нижній блок з кнопками"), default=True)
    cta_title_uk = models.CharField(
        _("Заголовок нижнього блоку [UA]"),
        max_length=160,
        blank=True,
        default="Готові знайти свій догляд?",
    )
    cta_title_ru = models.CharField(
        _("Заголовок нижнього блоку [RU]"),
        max_length=160,
        blank=True,
        default="Готовы найти свой уход?",
    )
    cta_text_uk = models.TextField(
        _("Текст нижнього блоку [UA]"),
        blank=True,
        default=(
            "Перегляньте каталог або напишіть нам — підкажемо за брендом, "
            "типом шкіри чи доставкою."
        ),
    )
    cta_text_ru = models.TextField(
        _("Текст нижнього блоку [RU]"),
        blank=True,
        default=(
            "Посмотрите каталог или напишите нам — подскажем по бренду, "
            "типу кожи или доставке."
        ),
    )
    cta_catalog_label_uk = models.CharField(
        _("Кнопка «До каталогу» [UA]"),
        max_length=80,
        blank=True,
        default="До каталогу",
    )
    cta_catalog_label_ru = models.CharField(
        _("Кнопка «До каталогу» [RU]"),
        max_length=80,
        blank=True,
        default="В каталог",
    )
    cta_contacts_label_uk = models.CharField(
        _("Кнопка «Контакти» [UA]"),
        max_length=80,
        blank=True,
        default="Контакти",
    )
    cta_contacts_label_ru = models.CharField(
        _("Кнопка «Контакти» [RU]"),
        max_length=80,
        blank=True,
        default="Контакты",
    )

    updated_at = models.DateTimeField(_("Оновлено"), auto_now=True)

    class Meta:
        verbose_name = _("Про нас — контент")
        verbose_name_plural = _("Про нас — контент")

    def __str__(self) -> str:
        return "AboutContent"

    def save(self, *args, **kwargs) -> None:
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs) -> tuple[int, dict]:
        return 0, {}

    @classmethod
    def load(cls) -> "AboutContent":
        obj, _created = cls.objects.get_or_create(pk=1)
        return obj

    def _loc(self, base: str) -> str:
        lang = (get_language() or "uk")[:2]
        uk = getattr(self, f"{base}_uk", "") or ""
        ru = getattr(self, f"{base}_ru", "") or ""
        if lang == "ru" and ru:
            return ru
        return uk or ru

    @property
    def hero_kicker(self) -> str:
        return self._loc("hero_kicker")

    @property
    def hero_title(self) -> str:
        return self._loc("hero_title")

    @property
    def hero_text(self) -> str:
        return self._loc("hero_text")

    @property
    def history_kicker(self) -> str:
        return self._loc("history_kicker")

    @property
    def history_title(self) -> str:
        return self._loc("history_title")

    @property
    def history_body(self) -> str:
        return self._loc("history_body")

    @property
    def history_cards(self) -> list[dict]:
        fallbacks = {
            1: "img/about/history-paper.png",
            2: "img/about/history-paper.png",
            3: "img/about/history-paper.png",
        }
        items: list[dict] = []
        for index in range(1, 4):
            title = self._loc(f"history_card_{index}_title")
            body = self._loc(f"history_card_{index}_body")
            if title or body:
                image_url = ""
                if index == 1 and self.history_image:
                    image_url = self.history_image.url
                elif index == 3 and self.philosophy_image:
                    image_url = self.philosophy_image.url
                items.append(
                    {
                        "n": index,
                        "title": title,
                        "body": body,
                        "image_url": image_url,
                        "fallback_static": fallbacks[index],
                    }
                )
        return items

    @property
    def philosophy_kicker(self) -> str:
        return self._loc("philosophy_kicker")

    @property
    def philosophy_title(self) -> str:
        return self._loc("philosophy_title")

    @property
    def philosophy_body(self) -> str:
        return self._loc("philosophy_body")

    @property
    def philosophy_theses(self) -> list[dict]:
        """До 4 цінностей для анімованого ряду."""
        items: list[dict] = []
        for index in range(1, 5):
            title = self._loc(f"philosophy_thesis_{index}_title")
            text = self._loc(f"philosophy_thesis_{index}_text")
            if title or text:
                items.append({"n": index, "title": title, "text": text})
        return items

    @property
    def cta_title(self) -> str:
        return self._loc("cta_title")

    @property
    def cta_text(self) -> str:
        return self._loc("cta_text")

    @property
    def cta_catalog_label(self) -> str:
        return self._loc("cta_catalog_label")

    @property
    def cta_contacts_label(self) -> str:
        return self._loc("cta_contacts_label")
