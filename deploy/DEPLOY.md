# DigitalOcean Droplet — OGEMED (oge.in.ua)
# Docker Compose: nginx + gunicorn + PostgreSQL
# Vault: django-digitalocean-deploy · django-docker-ssl · django-droplet-http-first

Шлях на сервері: `/var/www/ogemed`  
Репозиторій: `prometeylabsanna-lgtm/ogemed`  
Домен: `oge.in.ua` (+ `www.oge.in.ua`)

Архітектура:

```
Internet → nginx (:80/:443) → web:8000 (gunicorn) → Django
                ↳ /static/  → volume staticfiles
                ↳ /media/   → volume media
                ↳ db        → PostgreSQL 16
```

---

## Частина A — файли вже в репо (перевірка)

На Mac у корені проєкту мають бути:

| Файл | Призначення |
|------|-------------|
| `Dockerfile` | образ Django/gunicorn |
| `docker-compose.yml` | db + web + nginx (HTTP) |
| `docker-compose.prod.yml` | HTTPS + Let's Encrypt |
| `.dockerignore` | що не йде в образ |
| `.env.docker.example` | шаблон секретів |
| `config/settings/docker.py` | prod settings для Compose |
| `deploy/entrypoint.sh` | wait DB → migrate → collectstatic |
| `deploy/nginx/docker.conf` | HTTP |
| `deploy/nginx/docker.prod.conf` | HTTPS для oge.in.ua |
| `deploy/docker/install-docker.sh` | Docker на Ubuntu |
| `deploy/docker/deploy.sh` | build + up + healthz |

Перед деплоєм: закоміть і запуш ці файли в `main` (або свою гілку).

---

## Частина B — Mac: SSH-ключ для Droplet

### B1. Створити ключ (без passphrase)

Відкрий **Terminal** на Mac:

```bash
ssh-keygen -t ed25519 -f ~/.ssh/id_ogemed_do -N "" -C "ogemed-do"
chmod 600 ~/.ssh/id_ogemed_do
cat ~/.ssh/id_ogemed_do.pub
```

Скопіюй **весь** рядок `ssh-ed25519 AAAA... ogemed-do` (буде потрібен у DigitalOcean).

### B2. Додати ключ у DigitalOcean

1. Відкрий браузер → [https://cloud.digitalocean.com](https://cloud.digitalocean.com)
2. Увійди в акаунт
3. Ліворуч: **Settings** (або іконка аватара → **API** / **Settings**)
4. Вкладка **Security** → секція **SSH Keys**
5. Натисни **Add SSH Key**
6. У поле **SSH key content** встав публічний ключ з `cat ...pub`
7. **Name:** наприклад `ogemed-mac`
8. Натисни **Add SSH Key**

---

## Частина C — створити Droplet

1. У DO: ліворуч **Create** (зелена кнопка) → **Droplets**
2. **Region:** найближчий (наприклад Frankfurt / Amsterdam)
3. **Image:** вкладка **Ubuntu** → **24.04 (LTS) x64**
4. **Size:** мінімум **Basic → Regular → 2 GB RAM / 1 CPU** (магазин; 1 GB лише зі swap)
5. **Authentication:** **SSH Key** → постав галочку на `ogemed-mac` (не Password)
6. **Hostname:** `ogemed`
7. Натисни **Create Droplet**
8. Дочекайся зеленого статусу → скопіюй **IPv4** (кнопка копіювання біля IP)

### C1. Firewall (рекомендовано)

1. Ліворуч **Networking** → **Firewalls** → **Create Firewall**
2. Inbound rules:
   - SSH TCP **22** — Sources: Your IP (або All якщо треба з будь-де)
   - HTTP TCP **80** — All IPv4 / All IPv6
   - HTTPS TCP **443** — All IPv4 / All IPv6
3. **Apply to Droplets** → вибери `ogemed` → **Create Firewall**

### C2. Аліас SSH на Mac

```bash
nano ~/.ssh/config
```

В кінець файлу (заміни `ТВІЙ_IP`):

```
Host ogemed
  HostName ТВІЙ_IP
  User root
  IdentityFile ~/.ssh/id_ogemed_do
  IdentitiesOnly yes
  ServerAliveInterval 30
  ServerAliveCountMax 3
```

Збережи: `Ctrl+O`, Enter, `Ctrl+X`.

Перевірка:

```bash
ssh ogemed
```

Має зайти без пароля. Далі всі команди «на сервері» — після `ssh ogemed`.

---

## Частина D — DNS для oge.in.ua

У панелі реєстратора домену (де куплено `oge.in.ua`):

1. Знайди **DNS / DNS-зона / Керування DNS**
2. Створи / зміни записи типу **A**:

| Host / Name | Type | Value | TTL |
|-------------|------|-------|-----|
| `@` (або порожньо) | A | IP Droplet | 300 |
| `www` | A | IP Droplet | 300 |

3. Збережи. Propagation: від кількох хвилин до кількох годин.

Перевірка з Mac:

```bash
dig +short oge.in.ua A
dig +short www.oge.in.ua A
```

Обидва мають показати IP Droplet.

---

## Частина E — перший деплой на сервері (HTTP)

На сервері (`ssh ogemed`):

### E1. Docker

```bash
mkdir -p /var/www
cd /var/www
git clone https://github.com/prometeylabsanna-lgtm/ogemed.git ogemed
cd /var/www/ogemed
bash deploy/docker/install-docker.sh
```

Якщо GitHub просить пароль — у поле Password встав **Personal Access Token** (GitHub → Settings → Developer settings → Personal access tokens), не пароль акаунта.

Або клонуй по SSH, якщо на Droplet додано deploy key.

### E2. `.env`

```bash
cd /var/www/ogemed
cp .env.docker.example .env
nano .env
```

Обовʼязково заповни:

1. `SECRET_KEY` — згенеруй на Mac або на сервері:
   ```bash
   python3 -c "import secrets; print(secrets.token_urlsafe(50))"
   ```
2. `POSTGRES_PASSWORD` — довгий випадковий пароль; **той самий** у `DATABASE_URL`
3. `DATABASE_URL=postgres://ogemed:ТОЙ_САМИЙ_ПАРОЛЬ@db:5432/ogemed`
4. `ALLOWED_HOSTS` — **заміни** слово `DROPLET_IP` на реальний IPv4, наприклад:
   ```
   ALLOWED_HOSTS=oge.in.ua,www.oge.in.ua,203.0.113.10,127.0.0.1,localhost,web
   ```
5. Поки SSL ще немає (перший HTTP-тест):
   ```
   CSRF_TRUSTED_ORIGINS=http://oge.in.ua,http://www.oge.in.ua,http://ТВІЙ_IP
   SESSION_COOKIE_SECURE=False
   CSRF_COOKIE_SECURE=False
   SITE_URL=http://oge.in.ua
   SECURE_HSTS_SECONDS=0
   ```

Збережи nano: `Ctrl+O`, Enter, `Ctrl+X`.

Перевірка що немає літерала:

```bash
grep ALLOWED_HOSTS .env
# погано: ...DROPLET_IP...
# добре: ...203.0.113.10... (твій IP)
```

### E3. Підняти стек (HTTP)

```bash
cd /var/www/ogemed
chmod +x deploy/entrypoint.sh deploy/docker/*.sh
bash deploy/docker/deploy.sh
```

Очікуй `healthz HTTP OK`. Якщо ні:

```bash
docker compose -f docker-compose.yml ps
docker compose -f docker-compose.yml logs --tail=80 web
```

Перевірки:

```bash
curl -sf http://127.0.0.1/healthz/ && echo OK
curl -sI -H "Host: oge.in.ua" http://127.0.0.1/ | head -5
```

У браузері: `http://oge.in.ua/` або `http://ТВІЙ_IP/` (Host має бути в `ALLOWED_HOSTS`).

### E4. Суперюзер

```bash
cd /var/www/ogemed
docker compose -f docker-compose.yml exec web python manage.py createsuperuser
```

Адмінка: `http://oge.in.ua/<ADMIN_URL>/` (значення з `.env`, не `/admin/`).

### E5. Демо-каталог + картинки (обовʼязково на порожній БД)

Volume `media` спочатку порожній — спочатку скопіюй seed у контейнер, потім seed:

```bash
cd /var/www/ogemed
# HTTP-стек:
COMPOSE="docker compose -f docker-compose.yml"
# після SSL:
# COMPOSE="docker compose -f docker-compose.yml -f docker-compose.prod.yml"

$COMPOSE exec web mkdir -p /app/media/seed
$COMPOSE cp media/seed/. web:/app/media/seed/
$COMPOSE exec web python manage.py seed_demo
$COMPOSE exec web python manage.py seed_site_blocks
```

Перевірка: `https://oge.in.ua/` — hero-фото, товар Bioactive Peptide Serum, блоки головної.  
Адмін `admin` від `createsuperuser` не чіпається. Після go-live не ганяти `seed_demo` знову (перезапише демо-контент).

---

## Частина F — HTTPS (Let's Encrypt)

DNS уже має вказувати на Droplet (див. Частина D).

```bash
cd /var/www/ogemed
apt update && apt install -y certbot

# Звільнити :80 для standalone
docker compose -f docker-compose.yml stop nginx

certbot certonly --standalone \
  -d oge.in.ua -d www.oge.in.ua \
  --agree-tos -m ТВІЙ@EMAIL.com

ls /etc/letsencrypt/live/oge.in.ua/
```

Онови `.env` після сертифіката:

```bash
nano .env
```

```
CSRF_TRUSTED_ORIGINS=https://oge.in.ua,https://www.oge.in.ua
SITE_URL=https://oge.in.ua
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
```

Прод-деплой (монтує `docker.prod.conf` + `/etc/letsencrypt`):

```bash
bash deploy/docker/deploy.sh --prod
```

Перевірки:

```bash
curl -sf https://oge.in.ua/healthz/ && echo HTTPS_OK
curl -sI https://oge.in.ua/ | head -8
docker compose -f docker-compose.yml -f docker-compose.prod.yml exec nginx ls /etc/letsencrypt/live/oge.in.ua/
```

У браузері: `https://oge.in.ua/` — замок, CSS з `/static/`, логін в адмінку тримається.

### F1. Автооновлення сертифіката

```bash
crontab -e
```

Додай рядок:

```
0 3 * * * certbot renew --quiet && cd /var/www/ogemed && docker compose -f docker-compose.yml -f docker-compose.prod.yml exec -T nginx nginx -s reload
```

---

## Частина G — оновлення коду (після змін у git)

**`git push` ≠ live.** На сервері:

```bash
ssh ogemed
cd /var/www/ogemed
git pull origin main
bash deploy/docker/deploy.sh --prod
```

Якщо змінювали лише `.env`:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --force-recreate web
```

Не редагуй `docker-compose*.yml` / nginx / settings вручну на Droplet — лише через git (інакше `git pull` падає).

---

## Частина H — чеклист go-live

- [ ] `.env` на сервері, не в git
- [ ] Немає літерала `DROPLET_IP` у `.env`
- [ ] `DEBUG=False`, `DJANGO_SETTINGS_MODULE=config.settings.docker`
- [ ] `ALLOWED_HOSTS`: домен, www, IP, `127.0.0.1`, `localhost`, `web`
- [ ] Після SSL: cookies Secure=True, `CSRF_TRUSTED_ORIGINS` з `https://`
- [ ] `SECURE_SSL_REDIRECT=False` у docker settings (уже в коді)
- [ ] Host nginx/gunicorn зупинені (`deploy.sh` робить це)
- [ ] `https://oge.in.ua/healthz/` → 200
- [ ] CSS/JS з `/static/`, media після рестарту
- [ ] Адмінка логінить, кошик тримає сесію
- [ ] Firewall: 22, 80, 443
- [ ] Backup Postgres (наприклад `docker compose exec db pg_dump ...`)

---

## Типові проблеми

| Симптом | Що зробити |
|---------|------------|
| 400 на сайті, healthz з localhost OK | У `.env` був `DROPLET_IP` → постав IPv4 → `--force-recreate web` |
| Кошик/адмін «не тримає» на HTTP | `SESSION_COOKIE_SECURE=False` до SSL |
| `web` unhealthy / 301 | Не вмикай `SECURE_SSL_REDIRECT` на Gunicorn |
| HTTPS не працює | Прод compose має `docker.prod.conf` + `:443` + `/etc/letsencrypt` |
| certbot fail | Спочатку `docker compose stop nginx` |
| 502 | `docker compose logs web` — чекай migrate/collectstatic |
| Port 80 in use | `systemctl stop nginx`; знову `deploy.sh` |
| Зміни коду «не видно» | Після `git pull` обовʼязково `build` (`deploy.sh` робить) |

Логи:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml logs -f --tail=100 web nginx
```

---

## Legacy (без Docker)

Старі приклади `deploy/nginx.conf.example` і `deploy/gunicorn.service.example` — лише для bare-metal. Для `oge.in.ua` використовуй цей Docker-гайд.
