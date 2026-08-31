#!/usr/bin/env bash
set -euo pipefail

echo "==> Entrypoint started"
cd /app

echo "==> Waiting for PostgreSQL..."
python <<'WAIT_DB'
import os
import sys
import time

import psycopg2

db_url = os.environ.get("DATABASE_URL", "")
if not db_url:
    print("==> DATABASE_URL not set, skipping DB wait")
    sys.exit(0)

for attempt in range(30):
    try:
        conn = psycopg2.connect(db_url)
        conn.close()
        print(f"==> DB ready (attempt {attempt + 1})")
        sys.exit(0)
    except psycopg2.OperationalError as exc:
        print(f"  {attempt + 1}/30: {exc}")
        time.sleep(2)

print("==> FATAL: Database not ready after 60s")
sys.exit(1)
WAIT_DB

echo "==> Django check"
python manage.py check --deploy || true

echo "==> Migrations"
python manage.py migrate --noinput

echo "==> Compile messages"
python manage.py compilemessages -l uk -l ru 2>/dev/null || true

echo "==> Collect static"
python manage.py collectstatic --noinput

_static_count=$(find "${STATIC_ROOT:-/app/staticfiles}" -type f 2>/dev/null | wc -l | tr -d ' ')
echo "==> static files: ${_static_count}"
if [ "${_static_count:-0}" -lt 10 ]; then
  echo "WARN: staticfiles count low — перевір STATIC_ROOT і collectstatic"
fi

echo "==> Starting: $*"
exec "$@"
