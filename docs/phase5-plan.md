# Phase 5 — Observability plan

_Written: 2026-04-06. Do not implement until scrape run 2 completes._

---

## 1. structlog setup

### Where to configure

Single call site: `src/logging_config.py` (new file).  
Called once from `src/scraper/__main__.py` (already the CLI entry point) before `asyncio.run(...)`.

Nothing else needs to import it — structlog's `configure()` is global.

### Format strategy

| Environment | Format | Trigger |
|---|---|---|
| Dev (`LOG_FORMAT=pretty` or no env var) | Colored, human-readable via `ConsoleRenderer` | default |
| Prod (`LOG_FORMAT=json`) | One JSON object per line via `JSONRenderer` | set in `.env` or docker-compose |

```python
# src/logging_config.py  (pseudocode — not final)
import os, structlog, logging

def configure_logging(level: str = "INFO") -> None:
    log_format = os.getenv("LOG_FORMAT", "pretty")

    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    if log_format == "json":
        renderer = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=shared_processors + [renderer],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, level.upper())
        ),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
```

### Modules that need logging replaced

All existing modules use `logging.getLogger(__name__)` + `logger.info(...)`.  
Replace each with `structlog.get_logger()` and switch to keyword args for structured fields:

| Module | Current | After |
|---|---|---|
| `src/scraper/pipeline.py` | `logger.info("Collected %d IDs", n)` | `log.info("ids_collected", count=n)` |
| `src/scraper/pipeline.py` | `logger.info("Scrape run %s complete — found=…")` | `log.info("scrape_complete", found=…, new=…, updated=…)` |
| `src/scraper/paginator.py` | `logger.info("Page %d/%d — %d listings")` | `log.info("page_fetched", page=n, total=t, found=k)` |
| `src/scraper/parser.py` | `logger.debug(…)` | `log.debug("listing_parsed", id=…)` |
| `src/scraper/browser.py` | retry/backoff messages | `log.warning("retry", attempt=n, url=…, status=…)` |

Key structured fields to emit consistently:
- `scrape_run_id` — bind to context at run start so every log line carries it
- `listing_id` / `sreality_id` — bind per-listing loop iteration
- `duration_ms` — for any timed operation (page fetch, detail fetch, DB write)

Use `structlog.contextvars.bind_contextvars(scrape_run_id=str(run.id))` once the run opens, so all subsequent log calls automatically include it without passing it around.

---

## 2. Scrape run monitoring — additional DB fields

Current `scrape_runs` columns are sufficient for correctness tracking. These additions would make it useful for performance monitoring:

### Proposed new columns (one migration)

| Column | Type | Purpose |
|---|---|---|
| `listings_skipped` | `int` | Listings where `fetch_listing_detail()` returned `None` — currently only tracked as error strings, not as a count |
| `avg_detail_fetch_ms` | `int nullable` | Mean time per detail fetch request (both 301 + 200). Flags if sreality slows down or we get throttled |
| `total_duration_s` | `int nullable` | `EXTRACT(EPOCH FROM finished_at - started_at)` — derivable but convenient to have pre-computed |
| `pages_fetched` | `int` | Number of search result pages paginated — useful to confirm full coverage |

**Implementation note:** `avg_detail_fetch_ms` and `pages_fetched` are accumulated in `ScrapeRunData` (Python-side) and written at `close_scrape_run()`. No live DB writes needed during the run.

### No-migration alternative (simpler)

Keep the schema as-is and compute the extra metrics from `errors` (JSONB) and the `started_at`/`finished_at` diff. Add a view:

```sql
CREATE VIEW scrape_run_summary AS
SELECT
    id,
    status,
    started_at,
    finished_at,
    EXTRACT(EPOCH FROM finished_at - started_at)::int AS duration_s,
    listings_found,
    listings_new,
    listings_updated,
    listings_found - listings_new - listings_updated AS listings_unchanged,
    CASE WHEN jsonb_typeof(errors) = 'array'
         THEN jsonb_array_length(errors) ELSE 0 END AS error_count
FROM scrape_runs;
```

This avoids a migration and gives the same information. **Preferred approach for now.**

---

## 3. Failure alerting

Two tiers — implement both, second tier is optional:

### Tier 1: failed_runs.log (always on)

When `close_scrape_run()` is called with `status="failed"`, append a line to `logs/failed_runs.log`:

```
2026-04-06T21:00:00Z  run_id=abc123  found=2471  errors=1  first_error="UniqueViolationError..."
```

Implementation: a small helper in `src/scraper/pipeline.py` (or `repository.py`), called from the `except` block. No new dependency.

### Tier 2: email via smtplib (opt-in)

If `ALERT_EMAIL` is set in `.env`, send one email per failed run:

```python
# src/alerts/email.py  (new, ~30 lines)
import os, smtplib
from email.message import EmailMessage

def send_failure_alert(run_id: str, error_summary: str) -> None:
    to = os.getenv("ALERT_EMAIL")
    if not to:
        return
    smtp_host = os.getenv("SMTP_HOST", "localhost")
    smtp_port = int(os.getenv("SMTP_PORT", "25"))
    msg = EmailMessage()
    msg["Subject"] = f"[sreality-scraper] Scrape run failed: {run_id}"
    msg["From"] = os.getenv("SMTP_FROM", "scraper@localhost")
    msg["To"] = to
    msg.set_content(f"Scrape run {run_id} failed.\n\n{error_summary}")
    with smtplib.SMTP(smtp_host, smtp_port) as s:
        s.send_message(msg)
```

New `.env` keys to document in `.env.example`:
```
ALERT_EMAIL=          # leave blank to disable
SMTP_HOST=localhost
SMTP_PORT=25
SMTP_FROM=scraper@localhost
```

No external service, no new pip dependency. Works with any local MTA or a Gmail relay.

---

## 4. Health check script

**File:** `scripts/healthcheck.py`  
**Purpose:** Called by cron, Docker `HEALTHCHECK`, or a human after a run.  
**Exit codes:** `0` = last run succeeded, `1` = failed/running too long/no runs.

```python
#!/usr/bin/env python3
"""Health check: prints last scrape run status, exits 0 (ok) or 1 (problem).

Usage:
    python scripts/healthcheck.py
    python scripts/healthcheck.py --max-age-hours 25   # alert if no run in 25h
"""
import argparse, asyncio, os, sys
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()

MAX_AGE_HOURS_DEFAULT = 25   # alert if last SUCCESS is older than this

async def check() -> int:
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import create_async_engine

    engine = create_async_engine(os.environ["DATABASE_URL"])
    async with engine.connect() as conn:
        row = (await conn.execute(
            text("""
                SELECT id, status, started_at, finished_at,
                       listings_found, listings_new, listings_updated,
                       CASE WHEN jsonb_typeof(errors) = 'array'
                            THEN jsonb_array_length(errors) ELSE 0 END AS error_count
                FROM scrape_runs
                ORDER BY started_at DESC LIMIT 1
            """)
        )).one_or_none()
    await engine.dispose()

    if row is None:
        print("UNKNOWN  no scrape runs in database")
        return 1

    age = datetime.now(timezone.utc) - row.started_at
    age_h = age.total_seconds() / 3600

    summary = (
        f"status={row.status}  "
        f"found={row.listings_found}  new={row.listings_new}  "
        f"updated={row.listings_updated}  errors={row.error_count}  "
        f"age={age_h:.1f}h"
    )

    if row.status == "success" and age_h <= MAX_AGE_HOURS_DEFAULT:
        print(f"OK       {summary}")
        return 0
    elif row.status == "running":
        # Running is ok if it started recently (< 3h); stale otherwise
        if age_h < 3:
            print(f"RUNNING  {summary}")
            return 0
        else:
            print(f"STALE    {summary}  (running for {age_h:.1f}h — possible hang)")
            return 1
    else:
        print(f"FAIL     {summary}")
        return 1


def main() -> None:
    sys.exit(asyncio.run(check()))

if __name__ == "__main__":
    main()
```

**Docker HEALTHCHECK integration** (add to `docker-compose.yml` app service later):
```yaml
healthcheck:
  test: ["CMD", "python", "scripts/healthcheck.py"]
  interval: 1h
  timeout: 10s
  retries: 1
  start_period: 30s
```

---

## Implementation order for Phase 5

1. `src/logging_config.py` — structlog configure, dev/prod toggle
2. Replace `logging.getLogger` in all 4 modules, add `bind_contextvars`
3. Create `scrape_run_summary` view (no migration needed)
4. `scripts/healthcheck.py` — standalone, no src/ changes
5. `logs/failed_runs.log` appender in pipeline.py
6. `src/alerts/email.py` + `.env.example` additions (opt-in, last)

---

## Open questions (decide before implementing)

- **structlog vs stdlib bridge:** httpx uses stdlib logging. Worth routing it through the structlog stdlib bridge so its output also goes to JSON? Probably yes — one line in `logging_config.py`.
- **`listings_skipped` count:** Currently a skipped listing only leaves an error string. Should we track skipped count separately in `ScrapeRunData`, or is the `errors` list length sufficient? Separate counter is cleaner for the health check.
- **Log rotation:** `logs/failed_runs.log` and `logs/scraper.log` will grow unbounded. Add `logging.handlers.RotatingFileHandler` or rely on Docker log rotation?
