#!/usr/bin/env bash
# Dump the postgres database to /backups/ and rotate old files.
#
# Crontab entry:
#   0 3 * * * /opt/sreality/scripts/backup_db.sh >> /opt/sreality/logs/cron.log 2>&1
#
# Backup file: /opt/sreality/backups/sreality_YYYY-MM-DD.sql.gz
# Retention:   7 days (older files are deleted automatically)

set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
COMPOSE="docker compose -f $REPO_DIR/docker-compose.prod.yml"
BACKUP_DIR="$REPO_DIR/backups"
DB_USER="${POSTGRES_USER:-sreality}"
DB_NAME="${POSTGRES_DB:-sreality}"
KEEP_DAYS=7

cd "$REPO_DIR"

mkdir -p "$BACKUP_DIR"

DATESTAMP="$(date -u +"%Y-%m-%d")"
OUTFILE="$BACKUP_DIR/sreality_${DATESTAMP}.sql.gz"

echo "[backup] $(date -u +"%Y-%m-%dT%H:%M:%SZ") dumping $DB_NAME → $OUTFILE"

$COMPOSE exec -T db \
    pg_dump -U "$DB_USER" "$DB_NAME" \
    | gzip > "$OUTFILE"

echo "[backup] dump complete ($(du -sh "$OUTFILE" | cut -f1))"

# Rotate: delete backups older than KEEP_DAYS
find "$BACKUP_DIR" -name "sreality_*.sql.gz" -mtime "+$KEEP_DAYS" -delete
echo "[backup] rotated files older than ${KEEP_DAYS} days"
