#!/usr/bin/env bash
# Deploy / update the sreality scraper on the production server.
#
# Handles both first-time setup and subsequent updates:
#   - First run: creates .env reminder, restores migration backup if present
#   - Every run: git pull, rebuild image, run migrations
#
# Usage:
#   cd /opt/sreality && bash scripts/deploy.sh

set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
COMPOSE="docker compose -f $REPO_DIR/docker-compose.prod.yml"
BACKUP_DIR="$REPO_DIR/backups"

cd "$REPO_DIR"

# --- 1. .env guard --------------------------------------------------------

if [ ! -f "$REPO_DIR/.env" ]; then
    echo "[deploy] WARNING: .env not found. Creating from .env.example..."
    cp "$REPO_DIR/.env.example" "$REPO_DIR/.env"
    echo ""
    echo "  !! ACTION REQUIRED !!"
    echo "  Edit .env and set POSTGRES_PASSWORD and DATABASE_URL before continuing:"
    echo "    nano $REPO_DIR/.env"
    echo ""
    echo "  Minimum required vars:"
    echo "    POSTGRES_PASSWORD=<strong-random-password>"
    echo "    DATABASE_URL=postgresql+asyncpg://sreality:<password>@db:5432/sreality"
    echo "    DATABASE_URL_SYNC=postgresql+psycopg2://sreality:<password>@db:5432/sreality"
    echo "    LOG_FORMAT=json"
    echo ""
    echo "  Generate a password with:  openssl rand -base64 16"
    echo ""
    exit 1
fi

# Load .env — parse manually to handle values with special shell characters
# (e.g. SCRAPE_USER_AGENT contains parentheses which break `source`)
while IFS='=' read -r key value; do
    [[ -z "$key" || "$key" =~ ^# ]] && continue
    value="${value%%#*}"
    value="${value#"${value%%[![:space:]]*}"}"
    value="${value%"${value##*[![:space:]]}"}"
    export "$key=$value"
done < "$REPO_DIR/.env"

# --- 2. Pull latest code --------------------------------------------------

echo "[deploy] Pulling latest code..."
git pull --ff-only

# --- 3. Build image -------------------------------------------------------

echo "[deploy] Building scraper image..."
$COMPOSE build scraper

# --- 4. Start database ----------------------------------------------------

echo "[deploy] Starting database..."
$COMPOSE up -d db

echo "[deploy] Waiting for postgres to be ready..."
for i in $(seq 1 30); do
    if $COMPOSE exec -T db pg_isready -U "${POSTGRES_USER:-sreality}" -q; then
        break
    fi
    echo "[deploy]   waiting... ($i/30)"
    sleep 2
done

# --- 5. Run migrations ----------------------------------------------------

echo "[deploy] Running database migrations..."
$COMPOSE run --rm --no-deps \
    scraper \
    alembic upgrade head

# --- 6. Restore migration backup (first-time only) ------------------------

MIGRATION_BACKUP="$(ls -t "$BACKUP_DIR"/migration_*.sql.gz 2>/dev/null | head -1 || true)"

if [ -n "$MIGRATION_BACKUP" ]; then
    # Check if listings table is empty — only restore on a fresh DB
    ROW_COUNT="$($COMPOSE exec -T db psql -U "${POSTGRES_USER:-sreality}" \
        "${POSTGRES_DB:-sreality}" -tAc "SELECT COUNT(*) FROM listings;" 2>/dev/null || echo "0")"

    if [ "$ROW_COUNT" = "0" ]; then
        echo "[deploy] Empty database detected. Restoring migration backup: $MIGRATION_BACKUP"
        echo "[deploy] This may take several minutes for large dumps..."
        gunzip -c "$MIGRATION_BACKUP" \
            | $COMPOSE exec -T db psql -U "${POSTGRES_USER:-sreality}" "${POSTGRES_DB:-sreality}"
        echo "[deploy] Backup restored."

        # Verify row count after restore
        RESTORED="$($COMPOSE exec -T db psql -U "${POSTGRES_USER:-sreality}" \
            "${POSTGRES_DB:-sreality}" -tAc "SELECT COUNT(*) FROM listings;")"
        echo "[deploy] Listings after restore: $RESTORED"
    else
        echo "[deploy] Database already has $ROW_COUNT listings — skipping backup restore."
    fi
fi

# --- 7. Create directories ------------------------------------------------

echo "[deploy] Creating logs and backups directories..."
mkdir -p "$REPO_DIR/logs" "$BACKUP_DIR"

# --- 8. Health check ------------------------------------------------------

echo "[deploy] Running health check..."
if python "$REPO_DIR/scripts/healthcheck.py" 2>/dev/null; then
    echo "[deploy] Health check passed."
else
    echo "[deploy] Health check returned non-zero (no successful scrape run yet — this is normal on first deploy)."
fi

# --- Summary --------------------------------------------------------------

echo ""
echo "================================================================"
echo "  Deploy complete."
echo "================================================================"
echo ""

# Print listing count and last scrape run
$COMPOSE exec -T db psql -U "${POSTGRES_USER:-sreality}" "${POSTGRES_DB:-sreality}" -c \
    "SELECT
        (SELECT COUNT(*) FROM listings)          AS total_listings,
        (SELECT COUNT(*) FROM listings
          WHERE is_active = true)                AS active_listings,
        (SELECT status FROM scrape_runs
          ORDER BY started_at DESC LIMIT 1)      AS last_run_status,
        (SELECT started_at FROM scrape_runs
          ORDER BY started_at DESC LIMIT 1)      AS last_run_started;" 2>/dev/null || true

echo ""
echo "  Next steps:"
echo "    Set up cron:    crontab -e"
echo "    Run scraper:    bash scripts/run_nightly.sh"
echo "    Verify counts:  bash scripts/verify_migration.sh"
echo "    See full guide: docs/migration.md"
echo ""
