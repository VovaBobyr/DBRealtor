#!/usr/bin/env bash
# Verify that a DB backup (sreality_*.sql.gz) is CORRECT — not just intact.
#
# Usage:
#   bash scripts/backup_verify.sh /path/to/sreality_YYYY-MM-DD.sql.gz
#
# Exit 0  = backup passed all checks; a "<file>.ok" sidecar is written with the
#           listings row count (used by the next run for the drop-vs-previous check).
# Exit !0 = backup is missing, truncated, structurally wrong, or lost too many rows.
#
# Why this exists:
#   `gzip -t` + a minimum file size only prove the file is INTACT. They do NOT
#   catch a clean gzip of a WRONG database (empty/half-loaded, mid-migration,
#   pg_dump interrupted but gzip closed cleanly). Rotating on those would let a
#   run of bad-but-intact backups delete every good one — the "all backups are
#   wrong" case. This script gates rotation on content, not just integrity.
#
# Checks:
#   1. file exists
#   2. size >= MIN_SIZE_BYTES              (empty/failed dump)
#   3. gzip -t                             (corruption / truncation)
#   4. "PostgreSQL database dump complete" trailer present (pg_dump finished)
#   5. COPY block present for every required table
#   6. listings rows >= MIN_ROWS          (absolute floor)
#   7. listings rows >= PREV * DROP_RATIO  (sudden data loss vs last good backup)

set -euo pipefail

FILE="${1:-}"
if [[ -z "$FILE" ]]; then
    echo "[verify] ERROR: no file given. Usage: backup_verify.sh <file.sql.gz>"
    exit 2
fi

# --- tunables (override via env) ------------------------------------------
MIN_SIZE_BYTES="${MIN_SIZE_BYTES:-$((10 * 1024 * 1024))}"   # 10 MB
MIN_ROWS="${MIN_ROWS:-1000}"                                # absolute listings floor
DROP_RATIO_PCT="${DROP_RATIO_PCT:-80}"                      # >= 80% of previous good backup
REQUIRED_TABLES=(listings price_history scrape_runs)

BACKUP_DIR="$(cd "$(dirname "$FILE")" && pwd)"
BASENAME="$(basename "$FILE")"

echo "[verify] checking $BASENAME ..."

# 1. exists
if [[ ! -f "$FILE" ]]; then
    echo "[verify] FAIL: file not found: $FILE"
    exit 1
fi

# 2. minimum size
ACTUAL_BYTES="$(stat -c%s "$FILE")"
if (( ACTUAL_BYTES < MIN_SIZE_BYTES )); then
    echo "[verify] FAIL: only ${ACTUAL_BYTES} bytes (< ${MIN_SIZE_BYTES} minimum) — empty or failed dump"
    exit 1
fi

# 3. gzip integrity
if ! gzip -t "$FILE" 2>/dev/null; then
    echo "[verify] FAIL: gzip integrity check failed — corrupt or truncated file"
    exit 1
fi

# 4-6. single decompression pass: trailer, required tables, listings row count
#   awk prints: <listings_rows> <seen_listings> <seen_price_history> <seen_scrape_runs> <trailer>
read -r ROWS SEEN_L SEEN_PH SEEN_SR TRAILER < <(
    gunzip -c "$FILE" | awk '
        /^COPY public\.listings /       { in_l = 1; seen_l = 1; next }
        /^COPY public\.price_history /  { seen_ph = 1 }
        /^COPY public\.scrape_runs /    { seen_sr = 1 }
        in_l == 1 {
            if ($0 == "\\.") { in_l = 0 }
            else            { rows++ }
        }
        /PostgreSQL database dump complete/ { trailer = 1 }
        END {
            printf "%d %d %d %d %d\n", rows+0, seen_l+0, seen_ph+0, seen_sr+0, trailer+0
        }
    '
)

# 4. trailer
if [[ "$TRAILER" != "1" ]]; then
    echo "[verify] FAIL: missing 'PostgreSQL database dump complete' trailer — dump was truncated"
    exit 1
fi

# 5. required tables
declare -A SEEN=( [listings]="$SEEN_L" [price_history]="$SEEN_PH" [scrape_runs]="$SEEN_SR" )
for t in "${REQUIRED_TABLES[@]}"; do
    if [[ "${SEEN[$t]}" != "1" ]]; then
        echo "[verify] FAIL: no COPY block for required table '$t' — incomplete schema/data"
        exit 1
    fi
done

# 6. absolute row floor
if (( ROWS < MIN_ROWS )); then
    echo "[verify] FAIL: listings has only ${ROWS} rows (< ${MIN_ROWS} floor) — DB looks empty/half-loaded"
    exit 1
fi

# 7. drop vs previous good backup (newest existing .ok sidecar, other than this file's)
PREV_OK="$(ls -t "$BACKUP_DIR"/sreality_*.sql.gz.ok 2>/dev/null | grep -vxF "$FILE.ok" | head -1 || true)"
if [[ -n "$PREV_OK" && -s "$PREV_OK" ]]; then
    PREV_ROWS="$(head -1 "$PREV_OK" | tr -dc '0-9')"
    if [[ -n "$PREV_ROWS" ]] && (( PREV_ROWS > 0 )); then
        # integer math: ROWS*100 >= PREV_ROWS*DROP_RATIO_PCT
        if (( ROWS * 100 < PREV_ROWS * DROP_RATIO_PCT )); then
            echo "[verify] FAIL: listings dropped to ${ROWS} rows from ${PREV_ROWS} (< ${DROP_RATIO_PCT}% of previous good backup: $(basename "$PREV_OK"))"
            echo "[verify] refusing to trust this backup — a genuine large drop can be overridden by lowering DROP_RATIO_PCT for one run"
            exit 1
        fi
    fi
fi

# passed — record the row count as this backup's proof-of-good sidecar
echo "$ROWS" > "$FILE.ok"
echo "[verify] OK: $BASENAME — ${ROWS} listings rows, all tables present, dump complete ($(du -sh "$FILE" | cut -f1))"
