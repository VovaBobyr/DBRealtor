#!/usr/bin/env bash
# Deploy / update the sreality scraper on the production server.
#
# Run this once after cloning, and again whenever you git pull changes.
# Assumes: Docker + docker compose plugin installed, .env present in /opt/sreality/
#
# Usage:
#   cd /opt/sreality && bash scripts/deploy.sh

set -euo pipefail

COMPOSE="docker compose -f docker-compose.prod.yml"

echo "[deploy] Pulling latest code..."
git pull --ff-only

echo "[deploy] Building scraper image..."
$COMPOSE build scraper

echo "[deploy] Starting database..."
$COMPOSE up -d db

echo "[deploy] Waiting for postgres to be ready..."
# Poll pg_isready rather than sleeping a fixed time
for i in $(seq 1 30); do
    if $COMPOSE exec -T db pg_isready -U "${POSTGRES_USER:-sreality}" -q; then
        break
    fi
    echo "[deploy]   waiting... ($i/30)"
    sleep 2
done

echo "[deploy] Running database migrations..."
$COMPOSE run --rm --no-deps \
    scraper \
    alembic upgrade head

echo "[deploy] Creating logs and backups directories..."
mkdir -p logs backups

echo "[deploy] Deploy complete."
echo "[deploy] DB is running. Run the scraper manually with:"
echo "           bash scripts/run_nightly.sh"
echo "         Or set up cron — see docs/deployment.md"
