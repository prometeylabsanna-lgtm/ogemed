# Деплой на Vercel (тестовий продакшен)

## Демо без зовнішніх сервісів

На білді: SQLite + `seed_demo`. Медіа — seed з білду + аплоади в `/tmp`.

**Обмеження:** SQLite і файли в `/tmp` **не спільні між лямбдами**. Тому фото бренду з адмінки може з’явитись на хвилину і зникнути після оновлення сторінки — це не баг адмінки, а архітектура Vercel-демо.

## Постійна адмінка на Vercel (рекомендовано)

У Vercel → Settings → Environment Variables додайте **обидва** шари:

1. **Postgres** (Neon / Supabase): `DATABASE_URL=postgres://...`
2. **S3-сумісне сховище** (Cloudflare R2 / AWS S3 / DO Spaces):
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_STORAGE_BUCKET_NAME`
   - `AWS_S3_ENDPOINT_URL` (для R2)
   - `AWS_S3_CUSTOM_DOMAIN` (публічний CDN/URL бакету)
   - `AWS_S3_REGION_NAME=auto` (або регіон)

Після цього Redeploy. Аплоади з адмінки підуть у бакет, записи — у Postgres і **переживуть** refresh.

Без S3 навіть з Postgres файли знову опиняться в `/tmp` і зникнуть.

## Адмінка (логін)

- Логін: `admin`
- Пароль за замовчуванням: `admin`
- На демо-SQLite зміна пароля в UI не тримається між інстансами.

Свій пароль на демо: env `DEMO_ADMIN_PASSWORD` → Redeploy.

## Фото брендів

Лише через адмінку (`cover_image` / `showcase_image`). Seed їх не перезаписує.  
Разовий імпорт з файлів (локально/Droplet):  
`python3 manage.py import_brand_covers --src media/brands/sources`

Якщо в адмінці «поламане превʼю» — у БД лишився шлях до файлу, якого немає на цьому інстансі: поставте «Очистити» і завантажте знову (після Postgres+S3).

## Деплой

1. Закоміть `media/seed/` (і за потреби `media/brands/sources/`).
2. Vercel → Root = корінь репо.
3. Env (опційно): `DEMO_ADMIN_PASSWORD`, або `DATABASE_URL` + `AWS_*`.
4. Deploy → `https://<project>.vercel.app/` і `/healthz/`

Бойовий варіант без serverless: Droplet + Postgres + постійний `MEDIA_ROOT` (див. `deploy/DEPLOY.md`).

## Performance / PageSpeed

1. Env `STATIC_VERSION` — інкремент на релізі зі змінами CSS/JS.
2. Бандли збираються на білді (`build_static_bundles` → `collectstatic`).
3. Після підключення S3 — re-upload важких фото через адмінку (WebP + thumb).
4. PageSpeed mobile на головній — ціль ≥ 90.
