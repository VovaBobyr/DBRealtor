#!/usr/bin/env bash
# Verify today's DB backup, upload it to Backblaze B2 via rclone, then rotate the
# remote keeping only the newest N VERIFIED backups.
#
# Crontab entry (runs 15 min after backup_db.sh):
#   15 3 * * * cd /opt/DBRealtor/DBRealtor && bash scripts/backup_upload.sh >> logs/cron.log 2>&1
#
# Prerequisites:
#   - rclone installed (curl https://rclone.org/install.sh | sudo bash)
#   - rclone configured with a remote named "b2" for Backblaze B2:
#       rclone config create b2 b2 account YOUR_KEY_ID key YOUR_APP_KEY
#   - Backblaze bucket named "dbrealtor-backups" (private, created in B2 console)
#   - Application key scoped to that bucket only
#
# Remote path: b2:dbrealtor-backups/
# Retention:   KEEP_REMOTE newest VERIFIED backups (10 GB free tier ~= 76 files max)
#
# SAFETY MODEL — why this can't leave you with "all backups wrong":
#   - A backup is uploaded ONLY if backup_verify.sh says it is correct (structure,
#     required tables, row-count floor, and no sudden row drop vs the last good one).
#   - Remote rotation runs ONLY after a verified upload succeeds (set -e aborts first
#     on any failure). So a bad night uploads nothing AND deletes nothing.
#   - Rotation keeps the newest KEEP_REMOTE files by count, so the most recent good
#     backup is never pruned.

set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BACKUP_DIR="$REPO_DIR/backups"
REMOTE="b2:dbrealtor-backups"
KEEP_REMOTE=14

DATESTAMP="$(date -u +"%Y-%m-%d")"
FILE="$BACKUP_DIR/sreality_${DATESTAMP}.sql.gz"

echo "[upload] $(date -u +"%Y-%m-%dT%H:%M:%SZ") processing $FILE ..."

if [[ ! -f "$FILE" ]]; then
    echo "[upload] ERROR: backup file not found: $FILE"
    exit 1
fi

# --- gate on content verification -----------------------------------------
# backup_verify.sh writes "<FILE>.ok" (row count) on success and exits non-zero
# otherwise. set -e turns a failed verify into an aborted upload (and no rotation).
echo "[upload] verifying backup before upload..."
bash "$REPO_DIR/scripts/backup_verify.sh" "$FILE"

# --- upload the backup and its proof-of-good sidecar ----------------------
echo "[upload] uploading to $REMOTE ..."
rclone copy "$FILE" "$REMOTE/" --progress
rclone copy "$FILE.ok" "$REMOTE/" 2>/dev/null || true
echo "[upload] done: $(basename "$FILE")"

# --- safe rotation: keep the newest KEEP_REMOTE verified backups by COUNT --
# Filenames sort chronologically (sreality_YYYY-MM-DD.sql.gz), so a lexical sort
# is oldest-first. We only ever delete from the oldest end, never the newest.
mapfile -t REMOTE_FILES < <(rclone lsf "$REMOTE/" --include "sreality_*.sql.gz" | sort)
COUNT=${#REMOTE_FILES[@]}
echo "[upload] remote has $COUNT verified backup(s); keeping newest $KEEP_REMOTE"

if (( COUNT > KEEP_REMOTE )); then
    DELETE_N=$(( COUNT - KEEP_REMOTE ))
    for (( i = 0; i < DELETE_N; i++ )); do
        OLD="${REMOTE_FILES[$i]}"
        echo "[upload] rotating out old backup: $OLD"
        rclone deletefile "$REMOTE/$OLD" || true
        rclone deletefile "$REMOTE/$OLD.ok" 2>/dev/null || true
    done
    echo "[upload] rotated out $DELETE_N old backup(s)"
else
    echo "[upload] nothing to rotate"
fi
