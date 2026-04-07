#!/usr/bin/env bash
# Run one full scrape cycle and exit.
# Designed to be called by cron.
#
# Crontab entry:
#   0 2 * * * /opt/sreality/scripts/run_nightly.sh >> /opt/sreality/logs/cron.log 2>&1
#
# Exit codes:
#   0 — scraper exited cleanly
#   1 — scraper failed (check logs/failed_runs.log for details)

set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
COMPOSE="docker compose -f $REPO_DIR/docker-compose.prod.yml"

cd "$REPO_DIR"

echo "[run_nightly] $(date -u +"%Y-%m-%dT%H:%M:%SZ") starting scrape..."

if $COMPOSE run --rm scraper; then
    echo "[run_nightly] $(date -u +"%Y-%m-%dT%H:%M:%SZ") scrape complete."
    exit 0
else
    echo "[run_nightly] $(date -u +"%Y-%m-%dT%H:%M:%SZ") scrape FAILED — check logs/failed_runs.log"
    exit 1
fi
