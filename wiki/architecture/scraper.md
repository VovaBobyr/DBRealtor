# DBRealtor Scraper — Architecture

> Source: `/DBRealtor/`  
> Full ADRs: `/DBRealtor/docs/decisions.md`  
> Module breakdown: `/DBRealtor/docs/architecture.md`  
> Build progress: `/DBRealtor/docs/progress.md`

## Stack

| Component | Technology |
|---|---|
| Language | Python 3.12+ |
| HTTP client | httpx (async) |
| HTML/JSON parsing | `__NEXT_DATA__` JSON extraction (no HTML parsing needed) |
| ORM | SQLAlchemy 2.x async (asyncpg driver) |
| Migrations | Alembic |
| Scheduling | cron via `scripts/run_nightly.sh` |
| Containerisation | Docker + docker-compose |

## Key decisions

- **sreality.cz is Next.js SSR** — full data in `<script id="__NEXT_DATA__">` JSON. No Playwright needed.
- **CMP bypass**: `Accept: application/json` + `X-Requested-With: XMLHttpRequest` headers skip the consent redirect
- **Detail URL shortcut**: `/detail/prodej/byt/1+kk/x/{id}` — sreality redirects to canonical URL regardless of path prefix
- **Upsert strategy**: `pg_insert().on_conflict_do_update(index_elements=["sreality_id"])` — atomic, safe for concurrent runs

## Module structure

```
src/
├── scraper/
│   ├── browser.py      async httpx client, retry/backoff, CMP headers
│   ├── paginator.py    collects all listing IDs from search pages
│   ├── parser.py       detail page → ListingData (Pydantic model)
│   └── pipeline.py     orchestrates: paginate → parse → upsert
├── storage/
│   ├── models.py       ORM: Listing, PriceHistory, ScrapeRun
│   ├── repository.py   upsert_listing(), mark_inactive(), scrape_run mgmt
│   └── session.py      async engine + get_session()
├── analysis/
│   ├── queries.py      price_trend(), area_stats(), recent_listings()
│   └── alerts.py       new_listings_since(), price_drops_since()
└── alerts/
    └── email.py        optional SMTP alerts (ALERT_EMAIL in .env)
```

## Phases completed

- Phase 2: Tech decisions (httpx, no Playwright) ✅
- Phase 3: Scaffold, Alembic, docker-compose ✅
- Phase 4a: Scraper (browser, paginator, parser, pipeline) ✅
- Phase 4b: Storage (upsert, price history) ✅
- Phase 4c: Analysis layer ✅
- Phase 5: Observability (structlog, healthcheck, email alerts) ✅
- Phase 7: Deployment scripts ✅
- Phase 6: Data migration (old MySQL → new schema) ⏳
- Phase 8: Maintenance mode ⏳

## Test suite

```bash
cd DBRealtor
docker compose up -d db
pytest tests/ -v   # 44 tests
```
