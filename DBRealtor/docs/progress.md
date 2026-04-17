# Build progress

Update this file at the end of every Claude Code session.
Use checkboxes so the agent can track what's done.

---

## Phase 1 — Audit & requirements
- [ ] Document what old project scraped (fields, frequency, volumes)
- [ ] Identify pain points in old codebase
- [ ] Confirm target data: listing types, localities, frequency

## Phase 2 — Technology decisions ✅ COMPLETE
- [x] Inspect sreality.cz — **Next.js SSR**. Data in `__NEXT_DATA__` JSON. No JS needed. → ADR-002 resolved
- [x] Confirm scraping library choice — **httpx + json** (no parsel, no Playwright)
- [x] Finalise all ADRs in docs/decisions.md — ADR-002 through ADR-007 complete

## Phase 3 — Scaffold ✅ COMPLETE
- [x] Project directory structure created
- [x] pyproject.toml with all dependencies
- [x] docker-compose.yml (postgres + app)
- [x] .env.example with all env vars
- [x] .gitignore
- [x] Alembic initialised (alembic.ini + db/migrations/env.py)
- [x] Initial migration (listings, price_history, scrape_runs) — db/migrations/versions/0001_initial_schema.py
- [x] `alembic upgrade head` runs cleanly
- [x] pytest discovers tests/ without errors

## Phase 4a — Scraper ✅ COMPLETE
- [x] browser.py — async httpx client, XHR headers bypass CMP, retry w/ backoff
- [x] paginator.py — `get_all_listing_ids()`, pagination + `max_ids` early-exit
- [x] parser.py — `fetch_listing_detail()` → `ListingData` Pydantic model, full field mapping
- [x] pipeline.py — `run_scrape(dry_run=True)`, CLI: `python -m src.scraper --dry-run --limit N`
- [x] Unit tests: 25 passing (test_paginator.py × 10, test_parser.py × 15), no network calls
- [x] Fixtures: tests/fixtures/listing_detail.json, tests/fixtures/search_page.json

**Notes:**
- CMP bypass: `Accept: application/json` + `X-Requested-With: XMLHttpRequest` headers (cookie approach no longer sufficient)
- Detail URL shortcut: `/detail/prodej/byt/1+kk/x/{id}` → sreality 301-redirects to canonical URL regardless of path prefix
- `--limit N` stops pagination after N IDs (no need to page through all 200 pages for testing)

## Phase 4b — Storage / pipeline ✅ COMPLETE
- [x] .env created from .env.example (POSTGRES_PASSWORD=changeme)
- [x] docker compose up -d db — postgres running at localhost:5432
- [x] alembic upgrade head — all 3 tables + 3 enum types created (migration 0001 fixed)
- [x] models.py — Listing, PriceHistory, ScrapeRun ORM models
- [x] session.py — async SQLAlchemy engine + get_session()
- [x] repository.py — upsert_listing() atomic (pg_insert ON CONFLICT), mark_inactive(), open/close_scrape_run()
- [x] pipeline.py — DB write path + --dry-run working
- [x] Integration tests — tests/storage/test_repository.py (6 tests incl. concurrency regression)

**Bug fixed (2026-04-06):** `upsert_listing()` rewrote from SELECT+INSERT to `pg_insert().on_conflict_do_update(index_elements=["sreality_id"])`. Concurrent upsert test added and passing.

## Phase 4c — Analysis layer ✅ COMPLETE
- [x] queries.py — price_trend(), area_stats(), recent_listings()
- [x] alerts.py — new_listings_since(), price_drops_since()
- [x] src/analysis/__main__.py — CLI: price-trend, area-stats, recent, alerts sub-commands
- [x] tests/analysis/test_queries.py — 13 integration tests covering all functions

**Total test suite: 44 tests, all passing.**

## Phase 5 — Observability ✅ COMPLETE
- [x] structlog configured, JSON in prod / pretty in dev (`LOG_FORMAT` env var)
- [x] `src/logging_config.py` — single configure() call, stdlib bridge (httpx, sqlalchemy) included
- [x] `bind_contextvars(scrape_run_id=...)` in pipeline._run_with_db() — every log line carries it
- [x] Replace `logging.getLogger` in all 4 src modules with `structlog.get_logger()`
- [x] `scrape_run_summary` DB view — `duration_s`, `listings_unchanged`, `error_count` without migration
- [x] `logs/failed_runs.log` appender — written by pipeline._append_failed_run_log() on status=failed
- [x] `src/alerts/email.py` — opt-in smtplib alert, activated by `ALERT_EMAIL` in .env
- [x] `scripts/healthcheck.py` — exits 0 (ok) / 1 (problem), Docker HEALTHCHECK compatible
- [x] `.env.example` updated with ALERT_EMAIL / SMTP_* vars

**Open questions resolved:**
- httpx stdlib logs → routed through structlog ProcessorFormatter bridge ✓
- `listings_skipped` → tracked in pipeline (separate counter, logged in scrape_complete event) ✓
- Log rotation → Docker log rotation for main log; failed_runs.log is append-only (low volume) ✓

**Total test suite: 44 tests, all passing.**

## Phase 6 — Data migration
- [ ] Script to read old MySQL dump
- [ ] Map old schema fields to new schema
- [ ] Validate row counts and spot-check data
- [ ] Backfill price_history from old records

## Phase 7 — Testing & deployment ✅ COMPLETE
- [x] Full test suite passing — 44/44 (2026-04-06)
- [x] docker compose up starts everything cleanly
- [x] Atomic upsert bug fixed — `UniqueViolationError` under concurrent scrapers resolved
- [x] `jsonb_array_length` scalar bug fixed in phase5-plan.md SQL (use `CASE WHEN jsonb_typeof`)
- [x] `Dockerfile` — Python 3.12-slim, installs deps, runs `python -m src.scraper`
- [x] `docker-compose.prod.yml` — postgres with named volume, scraper run-once, LOG_FORMAT=json, no public ports
- [x] `scripts/deploy.sh` — git pull, build, db up, alembic upgrade head
- [x] `scripts/run_nightly.sh` — single scrape run, designed for cron
- [x] `scripts/backup_db.sh` — pg_dump → gzip, 7-day rotation
- [x] `docs/deployment.md` — full DO setup guide, crontab, log viewing, update procedure
- [x] `.github/workflows/test.yml` — pytest on every push with postgres service container
- [ ] Verify final counts once scrape run 4 completes
- [ ] README with setup instructions

**Scrape run history:**
- Run 1 (`bed74751`): `--limit 10`, success, 10 found / 8 new / 2 updated
- Run 2 (`02aaa23e`): full, failed — UniqueViolationError from two concurrent processes (before fix)
- Run 3 (`11fbc313`): full, killed mid-run (198/4055), DB subsequently truncated
- Run 4 (`bw6orgi0m`): full, killed at ~303/4359 — migrating to DigitalOcean, will rerun there

## Phase 8 — Maintenance mode
- [ ] Monitoring in place
- [ ] Known fragile selectors documented
- [ ] Runbook for when sreality.cz changes its structure

---
_Last updated: 2026-04-06 — Phases 5 + 7 complete. Deploying to DigitalOcean. See docs/deployment.md._
