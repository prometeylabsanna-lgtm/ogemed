#!/usr/bin/env bash
# Deploy OGEMED on Droplet: free 80/443 → build → up → healthz.
# Usage (from /var/www/ogemed):
#   bash deploy/docker/deploy.sh              # HTTP (docker-compose.yml)
#   bash deploy/docker/deploy.sh --prod       # HTTPS (prod override)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

USE_PROD=0
if [[ "${1:-}" == "--prod" ]]; then
  USE_PROD=1
fi

COMPOSE=(docker compose -f docker-compose.yml)
if [[ "$USE_PROD" -eq 1 ]]; then
  COMPOSE=(docker compose -f docker-compose.yml -f docker-compose.prod.yml)
fi

free_host_ports() {
  echo "==> Freeing host ports 80/443 (bare-metal nginx/gunicorn)"
  systemctl stop nginx 2>/dev/null || true
  systemctl disable nginx 2>/dev/null || true
  systemctl stop 'gunicorn-*' 2>/dev/null || true
  systemctl disable 'gunicorn-*' 2>/dev/null || true
  systemctl stop ogemed 2>/dev/null || true
  systemctl disable ogemed 2>/dev/null || true
  if command -v fuser >/dev/null 2>&1; then
    fuser -k 80/tcp 2>/dev/null || true
    fuser -k 443/tcp 2>/dev/null || true
  fi
}

echo "==> Project: $ROOT"
free_host_ports

if [[ ! -f .env ]]; then
  echo "FATAL: .env missing. cp .env.docker.example .env && nano .env"
  exit 1
fi

if grep -qE 'ALLOWED_HOSTS=.*DROPLET_IP' .env 2>/dev/null; then
  echo "FATAL: .env still has literal DROPLET_IP — replace with real IPv4"
  exit 1
fi

echo "==> Building web image"
"${COMPOSE[@]}" build web

echo "==> Starting stack"
set +e
"${COMPOSE[@]}" up -d
_up_rc=$?
set -e
if [[ $_up_rc -ne 0 ]]; then
  echo "WARN: first up exited ${_up_rc} — waiting for health, then retry"
fi

echo "==> Waiting for /healthz/"
_ok=0
for i in $(seq 1 60); do
  if curl -sf -H "Host: 127.0.0.1" "http://127.0.0.1/healthz/" >/dev/null 2>&1 \
    || curl -sf "http://127.0.0.1:8000/healthz/" >/dev/null 2>&1; then
    _ok=1
    break
  fi
  # nginx proxy path (no Host needed for healthz if ALLOWED_HOSTS has localhost)
  if curl -sf "http://127.0.0.1/healthz/" >/dev/null 2>&1; then
    _ok=1
    break
  fi
  sleep 3
done

"${COMPOSE[@]}" up -d

echo "==> Inventory"
for svc in db web nginx; do
  if "${COMPOSE[@]}" ps --status running --services 2>/dev/null | grep -qx "$svc" \
    || "${COMPOSE[@]}" ps 2>/dev/null | grep -E "[[:space:]]${svc}[[:space:]]" | grep -Eqi 'Up|running|healthy'; then
    echo "  OK: $svc"
  else
    echo "  CHECK: $svc (див. docker compose ps)"
  fi
done

"${COMPOSE[@]}" ps

if [[ $_ok -eq 1 ]] || curl -sf "http://127.0.0.1/healthz/" >/dev/null 2>&1; then
  echo "==> healthz HTTP OK"
else
  echo "==> healthz not ready yet — logs:"
  "${COMPOSE[@]}" logs --tail=40 web nginx
  exit 1
fi

echo "==> Deploy finished"
