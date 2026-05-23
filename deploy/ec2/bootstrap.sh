#!/usr/bin/env bash

set -euo pipefail

APP_DIR="/opt/ai-resume-analyzer"

echo "Updating system packages..."
if command -v apt-get >/dev/null 2>&1; then
  sudo apt-get update -y
  sudo apt-get install -y ca-certificates curl git
elif command -v dnf >/dev/null 2>&1; then
  sudo dnf update -y
  sudo dnf install -y ca-certificates curl git
else
  echo "Unsupported package manager. Install Docker manually." >&2
  exit 1
fi

echo "Installing Docker..."
if ! command -v docker >/dev/null 2>&1; then
  curl -fsSL https://get.docker.com | sh
fi

echo "Starting Docker..."
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker "${USER}"

echo "Installing Docker Compose plugin if needed..."
if ! docker compose version >/dev/null 2>&1; then
  if command -v apt-get >/dev/null 2>&1; then
    sudo apt-get install -y docker-compose-plugin
  elif command -v dnf >/dev/null 2>&1; then
    sudo dnf install -y docker-compose-plugin
  fi
fi

echo "Creating app directory..."
sudo mkdir -p "${APP_DIR}"
sudo chown -R "${USER}:${USER}" "${APP_DIR}"

cat <<EOF

Bootstrap complete.

Next steps:
1. Copy your project into ${APP_DIR}
2. Create ${APP_DIR}/.env from .env.example
3. Run:
   cd ${APP_DIR}
   docker compose up --build -d

Log out and log back in before using Docker without sudo if group membership does not apply immediately.
EOF
