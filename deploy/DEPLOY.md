# DigitalOcean Droplet deploy notes (Nginx + Gunicorn + PostgreSQL)
# No Docker in MVP. Phase 2 infrastructure later: Redis + queue.

## First setup

1. Ubuntu 24.04 Droplet, create user / clone repo to `/var/www/ogemed`
2. Install: python3.12-venv, nginx, postgresql, certbot
3. Create Postgres DB/user; put `DATABASE_URL` in `.env`
4. `python3 -m venv .venv && pip install -r requirements.txt`
5. `cp .env.example .env` and fill secrets
6. `export DJANGO_SETTINGS_MODULE=config.settings.production`
7. `python manage.py migrate && python manage.py collectstatic --noinput`
8. `python manage.py seed_demo` (лише перший раз / демо-дані; пароль існуючого admin не чіпає)
9. Для бою краще: `python manage.py createsuperuser`
10. Copy `deploy/gunicorn.service.example` → `/etc/systemd/system/ogemed.service`
11. Copy `deploy/nginx.conf.example` → nginx site; reload nginx
12. `systemctl enable --now ogemed`
13. Certbot for TLS; set `CSRF_TRUSTED_ORIGINS` and `ALLOWED_HOSTS`
14. Health check: `curl -sf https://example.com/healthz/`

Пароль, змінений в адмінці, на Droplet **зберігається** (Postgres), на відміну від Vercel `/tmp` SQLite.

## Media

MVP: local `/var/www/media` (backups required).
Later: switch `STORAGES["default"]` to S3/Spaces without model changes.

## Updates

```bash
cd /var/www/ogemed
git pull
.venv/bin/pip install -r requirements.txt
.venv/bin/python manage.py migrate --noinput
.venv/bin/python manage.py collectstatic --noinput
sudo systemctl restart ogemed
```
