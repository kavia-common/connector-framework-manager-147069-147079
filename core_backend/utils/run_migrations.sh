#!/usr/bin/env bash
set -euo pipefail

# Usage: ./utils/run_migrations.sh [reset]
# If 'reset' is passed and using default SQLite DB, it will remove the local file.

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$HERE"

if [ ! -d "venv" ]; then
  python -m venv venv
fi

. venv/bin/activate

pip install -r requirements.txt

# Optional reset for SQLite default path
if [ "${1:-}" = "reset" ]; then
  # Detect SQLite default path from .env if present, else fallback
  DB_PATH="./connector_framework.db"
  if [ -f ".env" ]; then
    # Grep DATABASE_URL if sqlite and extract path after 'sqlite:///'
    RAW_URL="$(grep -E '^DATABASE_URL=sqlite' .env | tail -n1 | cut -d'=' -f2- || true)"
    if [ -n "$RAW_URL" ]; then
      DB_PATH="${RAW_URL#sqlite:///}"
    fi
  fi
  if [ -f "$DB_PATH" ]; then
    echo "Resetting local SQLite database at $DB_PATH"
    rm -f "$DB_PATH"
  fi
fi

alembic upgrade head
echo "Migrations applied successfully."
