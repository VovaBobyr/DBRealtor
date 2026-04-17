#!/usr/bin/env bash
# Verify that the migration to the new server transferred all data correctly.
#
# Usage:
#   bash scripts/verify_migration.sh
#   bash scripts/verify_migration.sh --expected-listings 4312 --expected-price-history 8200
#
# Exit codes:
#   0 — counts match expected values (within 1%) or no expected values given
#   1 — counts are outside the 1% tolerance, or DB is unreachable

set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
COMPOSE="docker compose -f $REPO_DIR/docker-compose.prod.yml"
DB_USER="${POSTGRES_USER:-sreality}"
DB_NAME="${POSTGRES_DB:-sreality}"

cd "$REPO_DIR"

# Load .env — parse manually to handle values with special shell characters
# (e.g. SCRAPE_USER_AGENT contains parentheses which break `source`)
if [ -f "$REPO_DIR/.env" ]; then
    while IFS='=' read -r key value; do
        [[ -z "$key" || "$key" =~ ^# ]] && continue
        value="${value%%#*}"
        value="${value#"${value%%[![:space:]]*}"}"
        value="${value%"${value##*[![:space:]]}"}"
        export "$key=$value"
    done < "$REPO_DIR/.env"
fi

# Parse optional --expected-* arguments
EXPECTED_LISTINGS=""
EXPECTED_PRICE_HISTORY=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --expected-listings)        EXPECTED_LISTINGS="$2";      shift 2 ;;
        --expected-price-history)   EXPECTED_PRICE_HISTORY="$2"; shift 2 ;;
        *) echo "Unknown argument: $1"; exit 1 ;;
    esac
done

echo "[verify] $(date -u +"%Y-%m-%dT%H:%M:%SZ") — migration verification"
echo ""

# --- DB connectivity ------------------------------------------------------

if ! $COMPOSE exec -T db pg_isready -U "$DB_USER" -q; then
    echo "[verify] ERROR: postgres container is not ready."
    exit 1
fi

# --- Row counts -----------------------------------------------------------

echo "[verify] Row counts on NEW server:"
$COMPOSE exec -T db psql -U "$DB_USER" "$DB_NAME" -c \
    "SELECT 'listings'      AS table_name, COUNT(*) AS row_count FROM listings
     UNION ALL
     SELECT 'price_history',               COUNT(*) FROM price_history
     UNION ALL
     SELECT 'scrape_runs',                 COUNT(*) FROM scrape_runs
     ORDER BY table_name;"

# Capture individual counts for comparison
ACTUAL_LISTINGS="$($COMPOSE exec -T db psql -U "$DB_USER" "$DB_NAME" -tAc \
    "SELECT COUNT(*) FROM listings;")"
ACTUAL_PRICE_HISTORY="$($COMPOSE exec -T db psql -U "$DB_USER" "$DB_NAME" -tAc \
    "SELECT COUNT(*) FROM price_history;")"

echo ""
echo "[verify] Active listings: $(
    $COMPOSE exec -T db psql -U "$DB_USER" "$DB_NAME" -tAc \
        "SELECT COUNT(*) FROM listings WHERE is_active = true;"
)"

# --- Last 3 scrape runs ---------------------------------------------------

echo ""
echo "[verify] Last 3 scrape runs:"
$COMPOSE exec -T db psql -U "$DB_USER" "$DB_NAME" -c \
    "SELECT id, status, started_at,
            listings_found, listings_new, listings_updated,
            CASE WHEN jsonb_typeof(errors) = 'array'
                 THEN jsonb_array_length(errors) ELSE 0 END AS error_count
     FROM scrape_runs ORDER BY started_at DESC LIMIT 3;"

# --- Compare against expected counts (within 1%) -------------------------

FAIL=0

check_count() {
    local label="$1"
    local actual="$2"
    local expected="$3"

    if [ -z "$expected" ]; then
        echo "[verify] $label: $actual (no expected value provided — skipping check)"
        return
    fi

    # Calculate 1% tolerance using awk (bash can't do floats)
    local ok
    ok="$(awk -v a="$actual" -v e="$expected" 'BEGIN {
        diff = (a > e) ? a - e : e - a;
        pct  = (e > 0) ? diff / e * 100 : 0;
        print (pct <= 1) ? "yes" : "no";
    }')"

    if [ "$ok" = "yes" ]; then
        echo "[verify] PASS  $label: actual=$actual expected=$expected"
    else
        echo "[verify] FAIL  $label: actual=$actual expected=$expected (>1% difference)"
        FAIL=1
    fi
}

echo ""
echo "[verify] Comparing against expected counts..."
check_count "listings"      "$ACTUAL_LISTINGS"      "$EXPECTED_LISTINGS"
check_count "price_history" "$ACTUAL_PRICE_HISTORY" "$EXPECTED_PRICE_HISTORY"

echo ""
if [ "$FAIL" -eq 0 ]; then
    echo "[verify] RESULT: OK — all checks passed."
    exit 0
else
    echo "[verify] RESULT: FAIL — one or more counts are outside the 1% tolerance."
    echo "[verify] Check whether the backup was complete and the restore finished without errors."
    exit 1
fi
