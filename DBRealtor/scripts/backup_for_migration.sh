#!/usr/bin/env bash
# One-shot backup of the postgres database for migration to a new server.
#
# Run on the OLD DigitalOcean server:
#   cd /opt/sreality && bash scripts/backup_for_migration.sh
#
# Output file: /opt/sreality/backups/migration_YYYY-MM-DD.sql.gz
# After it completes, the script prints the scp command to copy it to the
# new server. Replace NEW_SERVER_IP before running.

set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
COMPOSE="docker compose -f $REPO_DIR/docker-compose.prod.yml"
BACKUP_DIR="$REPO_DIR/backups"
DB_USER="${POSTGRES_USER:-sreality}"
DB_NAME="${POSTGRES_DB:-sreality}"

cd "$REPO_DIR"

# Load .env — parse manually to handle values with special shell characters
# (e.g. SCRAPE_USER_AGENT contains parentheses which break `source`)
if [ -f "$REPO_DIR/.env" ]; then
    while IFS='=' read -r key value; do
        # Skip blank lines and comments
        [[ -z "$key" || "$key" =~ ^# ]] && continue
        # Strip inline comments and surrounding whitespace from value
        value="${value%%#*}"
        value="${value#"${value%%[![:space:]]*}"}"
        value="${value%"${value##*[![:space:]]}"}"
        export "$key=$value"
    done < "$REPO_DIR/.env"
fi

mkdir -p "$BACKUP_DIR"

DATESTAMP="$(date -u +"%Y-%m-%d")"
OUTFILE="$BACKUP_DIR/migration_${DATESTAMP}.sql.gz"

echo "[backup-migration] $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo "[backup-migration] Dumping $DB_NAME to $OUTFILE ..."

# Verify the DB container is up
if ! $COMPOSE exec -T db pg_isready -U "$DB_USER" -q; then
    echo "[backup-migration] ERROR: postgres container is not ready. Start it with:"
    echo "  $COMPOSE up -d db"
    exit 1
fi

# Dump row counts before backup so we can verify later
echo "[backup-migration] Row counts before backup:"
$COMPOSE exec -T db psql -U "$DB_USER" "$DB_NAME" -c \
    "SELECT 'listings' AS tbl, COUNT(*) FROM listings
     UNION ALL
     SELECT 'price_history', COUNT(*) FROM price_history
     UNION ALL
     SELECT 'scrape_runs',   COUNT(*) FROM scrape_runs;"

# Run the dump
$COMPOSE exec -T db \
    pg_dump -U "$DB_USER" "$DB_NAME" \
    | gzip > "$OUTFILE"

FILESIZE="$(du -sh "$OUTFILE" | cut -f1)"
echo "[backup-migration] Dump complete. File: $OUTFILE ($FILESIZE)"

if [ "$FILESIZE" = "0" ] || [ ! -s "$OUTFILE" ]; then
    echo "[backup-migration] ERROR: output file is empty — something went wrong."
    exit 1
fi

echo ""
echo "================================================================"
echo "  Backup complete: $OUTFILE ($FILESIZE)"
echo "================================================================"
echo ""
echo "  Copy to new server (replace NEW_SERVER_IP):"
echo ""
echo "    scp $OUTFILE root@NEW_SERVER_IP:/opt/sreality/backups/"
echo ""
echo "  Then continue with Phase 3 of docs/migration.md."
echo ""
