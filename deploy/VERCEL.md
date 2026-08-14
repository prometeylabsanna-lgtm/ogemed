# Деплой на Vercel (тестовий продакшен)

Без платних env і без зовнішньої БД. На білді: SQLite + `seed_demo` (товари, hero, бренди, фото з `media/seed` і `media/brands/sources`). Картинки віддає сама function з `/media/`.

Замовлення/сесії на інстансі не зберігаються назавжди (диск `/tmp`). Це вітрина, не бойовий магазин.

## Деплой

1. Закоміть `media/seed/` і `media/brands/sources/` (вони більше не в `.gitignore`).
2. Репозиторій → [vercel.com/new](https://vercel.com/new), Root = корінь репо.
3. Env у Vercel **не потрібні**.
4. Deploy → `https://<project>.vercel.app/` і `/healthz/`

Пізніше на Droplet: Postgres + `DATABASE_URL` + постійний `MEDIA_ROOT` (див. `deploy/DEPLOY.md`).
