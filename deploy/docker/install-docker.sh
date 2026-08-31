#!/usr/bin/env bash
# Install Docker Engine + Compose plugin on Ubuntu 24.04 Droplet.
set -euo pipefail

if command -v docker >/dev/null 2>&1; then
  echo "==> Docker already installed: $(docker --version)"
  docker compose version || true
  exit 0
fi

echo "==> Installing Docker via get.docker.com"
curl -fsSL https://get.docker.com | sh
systemctl enable --now docker

echo "==> Docker: $(docker --version)"
docker compose version
echo "==> Done. Run deploy as root or add user to docker group."
