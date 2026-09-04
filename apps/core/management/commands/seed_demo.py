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
        settings_obj, created = SiteSettings.objects.get_or_create(pk=1)
        contact_defaults = {
            "phone": "+380664247233",
            "phone_2": "+380973086063",
            "email": "hello@ogemed.ua",
            "manager_email": "manager@ogemed.ua",
            "address_uk": "м. Запоріжжя, вул. Фортечна 92, офіс 201",
            "address_ru": "г. Запорожье, ул. Фортечная 92, офис 201",
            "work_hours_uk": "Пн–Пт 10:00–19:00, Сб 11:00–16:00",
            "work_hours_ru": "Пн–Пт 10:00–19:00, Сб 11:00–16:00",
            "map_embed_url": (
                "https://www.google.com/maps?q=47.828823,35.185549"
                "&z=17&hl=uk&output=embed"
            ),
            "telegram_url": "https://t.me/ogemed",
            "instagram_url": "https://instagram.com/infini.zp",
            "telegram_consultant_url": "https://t.me/ogemed",
        }
        if created:
            for field, value in contact_defaults.items():
                setattr(settings_obj, field, value)
            settings_obj.save()
            self.stdout.write(self.style.SUCCESS("Created SiteSettings"))
        else:
            filled = []
            for field, value in contact_defaults.items():
                if not (getattr(settings_obj, field, "") or "").strip():
                    setattr(settings_obj, field, value)
                    filled.append(field)
            if filled:
                settings_obj.save(update_fields=filled)
                self.stdout.write(
                    self.style.SUCCESS(
                        "Filled empty SiteSettings: " + ", ".join(filled)
                    )
                )
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
        from django.core.management import call_command

        call_command("seed_catalog")
        call_command("seed_brands")
        call_command("seed_info_sections")
        # Фото брендів для вітрини: дефолти з media/seed у seed_catalog
        # (лише якщо showcase порожній). Покриття каталогу — через адмінку /
        # разовий import_brand_covers.

    def _ensure_demo_admin(self) -> None:
        """Demo: створити admin, якщо немає. Пароль існуючого не чіпати.

        На Vercel пароль синхронізує ensure_vercel_demo_admin() з env.
        На DigitalOcean / локалі зміна пароля в адмінці зберігається в БД.
        """
        from django.contrib.auth import get_user_model

        from config.vercel_sqlite import demo_admin_password

        User = get_user_model()
        if User.objects.filter(username="admin").exists():
            self.stdout.write("Superuser admin already exists — password unchanged")
            return

        password = demo_admin_password()
        user = User.objects.create_superuser(
            username="admin",
            email="admin@ogemed.local",
            password=password,
        )
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save(update_fields=["is_staff", "is_superuser", "is_active"])
        self.stdout.write(
            self.style.SUCCESS("Created superuser admin (password from env or default)")
        )
