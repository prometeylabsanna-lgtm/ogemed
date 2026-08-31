# OGEMED for you

Інтернет-магазин косметики. Django 5 SSR + HTMX. Мови: uk (`/`), ru (`/ru/...`).

## Стек

- Python 3.12+ / Django 5.2
- Templates: Django HTML (SSR), Mobile First CSS, vanilla JS + HTMX
- DB: SQLite (local) / PostgreSQL (prod)
- Admin: базова Django Admin
- Email: Resend API · Notify: Telegram / Viber (best-effort)
- Оплата: LiqPay + COD · Доставка: Нова Пошта + курʼєр
- Deploy: DigitalOcean Droplet (Docker: nginx + gunicorn + PostgreSQL); опційно Vercel demo

**Фаза 2 інфраструктури — Redis + черга:** Django-Q2 підключено.
Увімкнення: `NOTIFY_USE_QUEUE=True` (+ опційно `REDIS_URL`). Воркер: `python manage.py qcluster`.
Без прапорця notify лишається sync після `transaction.on_commit`.

## Архітектурні рішення

1. **Category ↔ Product:** `primary_category` FK (breadcrumbs) + `categories` M2M.
2. **i18n контенту:** поля `*_uk` / `*_ru` + property; UI — gettext.
3. **URL категорій:** плаский `/katalog/<slug>/`, дерево через `parent`.
4. **Deploy:** Droplet + Docker Compose (nginx + gunicorn + Postgres); Vercel — лише демо.
5. **Thank-you security:** `access_token` / session / owner — без IDOR.
6. **Cart session:** лише `{variant_id: qty}`, ціни з БД.

## Швидкий старт

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py seed_demo
python manage.py createsuperuser
python manage.py runserver
```

- Вітрина: http://127.0.0.1:8000/
- Адмінка: секретний шлях з `ADMIN_URL` у `.env` (за замовчуванням `/ogm8k2x9p4qh7n/`). `/admin/` завжди віддає 404.
- Health: http://127.0.0.1:8000/healthz/

## Тести

```bash
python manage.py test
```

## Деплой

- Droplet (oge.in.ua): [deploy/DEPLOY.md](deploy/DEPLOY.md) — Docker Compose, SSL, покроково
- Vercel (демо): [deploy/VERCEL.md](deploy/VERCEL.md)

## URL (SITE_MAP)

`/` · `/katalog/` · `/katalog/<slug>/` · `/tovar/<slug>/` · `/poshuk/` · `/koshyk/` · `/oformlennya/` · `/dyakuyemo/` · CMS-інфо · `/vkhid/` · `/reyestratsiya/` · `/kabinet/...` · `/payments/liqpay/...` · `/healthz/` · `/ru/...`

## Review — покращення після MVP

1. Redis як брокер замість ORM (`REDIS_URL`) + окремий systemd unit для `qcluster`
2. django-csp + повний SECURE_* audit
3. Fragment cache header/footer ≤ 1 хв
4. Media → DigitalOcean Spaces; optional TTN creation after paid
5. Призначення менеджера: `python manage.py ensure_manager_group` + User → Groups → «Менеджер»
