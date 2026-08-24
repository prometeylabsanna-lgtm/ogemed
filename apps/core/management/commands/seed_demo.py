from django.core.management.base import BaseCommand

from apps.cms.about_content import AboutContent
from apps.cms.models import CMSPage
from apps.core.models import SiteSettings

# Сторінки, які seed перезаписує (контент інфо-сторінок у стилі контактів).
OVERWRITE_SLUGS = {
    "dostavka-i-oplata",
    "povernennya",
    "polityka-konfidentsiynosti",
    "publichna-oferta",
}

PAGES = [
    {
        "slug": "pro-nas",
        "page_key": "about",
        "title_uk": "Про нас",
        "title_ru": "О нас",
        "body_uk": (
            "OGEMED for you — інтернет-магазин косметики з турботою про вашу красу.\n\n"
            "Ми підбираємо якісні засоби та дбаємо про зручний сервіс доставки в Україні."
        ),
        "body_ru": (
            "OGEMED for you — интернет-магазин косметики с заботой о вашей красоте.\n\n"
            "Мы подбираем качественные средства и заботимся об удобной доставке в Украине."
        ),
        "sort_order": 10,
    },
    {
        "slug": "kontakty",
        "page_key": "contacts",
        "title_uk": "Контакти",
        "title_ru": "Контакты",
        "body_uk": (
            "Ми завжди на звʼязку: підберемо догляд, підкажемо щодо доставки "
            "або відповімо на запитання про бренди з каталогу.\n\n"
            "Напишіть у Telegram, зателефонуйте або залиште заявку на зворотний дзвінок — "
            "менеджер OGEMED for you відповість у робочі години."
        ),
        "body_ru": (
            "Мы всегда на связи: подберём уход, подскажем по доставке "
            "или ответим на вопросы о брендах из каталога.\n\n"
            "Напишите в Telegram, позвоните или оставьте заявку на обратный звонок — "
            "менеджер OGEMED for you ответит в рабочие часы."
        ),
        "sort_order": 20,
    },
    {
        "slug": "dostavka-i-oplata",
        "page_key": "shipping",
        "title_uk": "Доставка і оплата",
        "title_ru": "Доставка и оплата",
        "body_uk": (
            "Доставляємо замовлення Новою Поштою по всій Україні — у відділення, "
            "поштомат або курʼєром. Оплата карткою через LiqPay або при отриманні."
        ),
        "body_ru": (
            "Доставляем заказы Новой Почтой по всей Украине — в отделение, "
            "почтомат или курьером. Оплата картой через LiqPay или при получении."
        ),
        "sort_order": 30,
    },
    {
        "slug": "povernennya",
        "page_key": "returns",
        "title_uk": "Повернення",
        "title_ru": "Возврат",
        "body_uk": (
            "Косметика належної якості не підлягає обміну чи поверненню за "
            "законом. Якщо товар з браком, пошкоджений у дорозі або надіслано "
            "помилково — допоможемо замінити або повернути кошти."
        ),
        "body_ru": (
            "Косметика надлежащего качества не подлежит обмену или возврату по "
            "закону. Если товар с браком, повреждён в пути или отправлен "
            "ошибочно — поможем заменить или вернуть средства."
        ),
        "sort_order": 40,
    },
    {
        "slug": "polityka-konfidentsiynosti",
        "page_key": "privacy",
        "title_uk": "Політика конфіденційності",
        "title_ru": "Политика конфиденциальности",
        "body_uk": (
            "Пояснюємо, які дані збирає OGEMED for you, навіщо вони потрібні "
            "і як ви можете реалізувати свої права. Юридичні реквізити "
            "контролера будуть оновлені пізніше."
        ),
        "body_ru": (
            "Объясняем, какие данные собирает OGEMED for you, зачем они нужны "
            "и как вы можете реализовать свои права. Юридические реквизиты "
            "контроллера будут обновлены позже."
        ),
        "sort_order": 50,
    },
    {
        "slug": "publichna-oferta",
        "page_key": "offer",
        "title_uk": "Публічна оферта",
        "title_ru": "Публичная оферта",
        "body_uk": (
            "Договір купівлі-продажу товарів дистанційним способом. "
            "Оформлюючи замовлення на сайті, ви приймаєте умови цієї оферти. "
            "Повні реквізити продавця додамо після отримання офіційних даних."
        ),
        "body_ru": (
            "Договор купли-продажи товаров дистанционным способом. "
            "Оформляя заказ на сайте, вы принимаете условия этой оферты. "
            "Полные реквизиты продавца добавим после получения официальных данных."
        ),
        "sort_order": 60,
    },
]


class Command(BaseCommand):
    help = (
        "Idempotent seed: SiteSettings + CMS pages. "
        "Info pages (shipping/returns/privacy/offer) are overwritten."
    )

    def handle(self, *args, **options):
        settings_obj, created = SiteSettings.objects.get_or_create(
            pk=1,
            defaults={
                "phone": "+380 44 123 45 67",
                "email": "hello@ogemed.ua",
                "manager_email": "manager@ogemed.ua",
                "address_uk": "м. Київ, вул. Хрещатик, 1",
                "address_ru": "г. Киев, ул. Крещатик, 1",
                "work_hours_uk": "Пн–Пт 10:00–19:00, Сб 11:00–16:00",
                "work_hours_ru": "Пн–Пт 10:00–19:00, Сб 11:00–16:00",
                "map_embed_url": (
                    "https://www.openstreetmap.org/export/embed.html"
                    "?bbox=30.515,50.445,30.530,50.455&layer=mapnik"
                    "&marker=50.4501,30.5234"
                ),
                "telegram_url": "https://t.me/ogemed",
                "instagram_url": "https://instagram.com/ogemed",
                "telegram_consultant_url": "https://t.me/ogemed",
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS("Created SiteSettings"))
        else:
            self.stdout.write("SiteSettings already exists — skipped")

        created_count = 0
        updated_count = 0
        for data in PAGES:
            defaults = {
                "page_key": data["page_key"],
                "title_uk": data["title_uk"],
                "title_ru": data["title_ru"],
                "body_uk": data["body_uk"],
                "body_ru": data["body_ru"],
                "is_published": True,
                "sort_order": data["sort_order"],
            }
            obj, was_created = CMSPage.objects.get_or_create(
                slug=data["slug"],
                defaults=defaults,
            )
            if was_created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Created CMSPage: {data['slug']}"))
            elif data["slug"] in OVERWRITE_SLUGS:
                for field, value in defaults.items():
                    setattr(obj, field, value)
                obj.save()
                updated_count += 1
                self.stdout.write(self.style.SUCCESS(f"Updated CMSPage: {data['slug']}"))
            else:
                self.stdout.write(f"CMSPage {data['slug']} exists — skipped")

        about, about_created = AboutContent.objects.get_or_create(pk=1)
        if about_created:
            self.stdout.write(self.style.SUCCESS("Created AboutContent"))
        else:
            self.stdout.write("AboutContent already exists — skipped")

        self._ensure_demo_admin()

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. New pages: {created_count}, updated: {updated_count}"
            )
        )
        from django.conf import settings
        from django.core.management import call_command

        call_command("seed_catalog")
        call_command("seed_brands")
        sources = settings.BASE_DIR / "media" / "brands" / "sources"
        if sources.is_dir():
            call_command("import_brand_covers", src=str(sources))

    def _ensure_demo_admin(self) -> None:
        """Demo/Vercel: staff superuser admin / admin."""
        from django.contrib.auth import get_user_model

        User = get_user_model()
        user, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@ogemed.local",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        user.set_password("admin")
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save()
        if created:
            self.stdout.write(self.style.SUCCESS("Created superuser admin / admin"))
        else:
            self.stdout.write("Updated superuser admin / admin")
