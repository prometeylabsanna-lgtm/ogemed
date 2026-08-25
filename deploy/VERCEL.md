# Деплой на Vercel (тестовий продакшен)

Без платних env і без зовнішньої БД. На білді: SQLite + `seed_demo` (товари, hero, бренди, фото з `media/seed` і `media/brands/sources`). Картинки віддає сама function з `/media/`.

Замовлення/сесії на інстансі не зберігаються назавжди (диск `/tmp`). Це вітрина, не бойовий магазин.

## Адмінка (логін)

- Логін: `admin`
- Пароль за замовчуванням: `admin`
- **Зміна пароля в UI на Vercel не зберігається** (SQLite у `/tmp`, різні інстанси, білд знову кладе seed).

Щоб свій пароль на демо:

1. Vercel → Project → Settings → Environment Variables
2. Додайте `DEMO_ADMIN_PASSWORD` = ваш пароль
3. Redeploy

Після деплою вхід: `admin` + значення з `DEMO_ADMIN_PASSWORD`.

## Деплой

1. Закоміть `media/seed/` і `media/brands/sources/` (вони більше не в `.gitignore`).
2. Репозиторій → [vercel.com/new](https://vercel.com/new), Root = корінь репо.
3. За бажанням: env `DEMO_ADMIN_PASSWORD` (див. вище).
4. Deploy → `https://<project>.vercel.app/` і `/healthz/`

Пізніше на Droplet: Postgres + `DATABASE_URL` + постійний `MEDIA_ROOT` (див. `deploy/DEPLOY.md`).
