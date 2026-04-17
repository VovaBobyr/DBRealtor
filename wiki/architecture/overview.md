# System Architecture Overview

## What this system does

Collects real estate listing data from sreality.cz continuously, stores it in PostgreSQL with full price history, and exposes it as a read-only analytics web portal.

## Component diagram

```
sreality.cz (Czech real estate portal)
        │
        │  httpx + XHR headers
        ▼
┌─────────────────────┐
│   DBRealtor         │  /opt/DBRealtor on Contabo VPS
│   Python scraper    │  runs nightly via cron
│   (nightly cron)    │  scripts/run_nightly.sh
└────────┬────────────┘
         │ SQLAlchemy async (upsert)
         ▼
┌─────────────────────┐
│   PostgreSQL        │  Docker container: dbrealtor_db
│   (sreality DB)     │  named volume: postgres_data
│                     │  port: 5432 (internal only)
└────────┬────────────┘
         │ SQLAlchemy async (read-only)
         ▼
┌─────────────────────┐
┌─────────────────────┐
│   DBRealtorWeb      │  /opt/DBRealtorWeb on Contabo VPS
│   FastAPI backend   │  :8000 (internal, behind nginx)
│   React frontend    │  :80 (public)
└─────────────────────┘
```

## Data flow

1. **Scrape run** (nightly): `paginator` collects all listing IDs → `parser` fetches each detail → `repository.upsert_listing()` inserts/updates → `scrape_runs` table records metadata
2. **Price change**: if `price_czk` changes on upsert, `price_history` row is inserted automatically
3. **Web request**: browser → nginx → FastAPI → SQLAlchemy async read → JSON response → React render

## Key tables

| Table | Owner | Purpose |
|---|---|---|
| `listings` | DBRealtor | One row per listing, updated each scrape |
| `price_history` | DBRealtor | Appended whenever price changes |
| `scrape_runs` | DBRealtor | Metadata per scrape execution |

Full schema: `../../DBRealtor/docs/architecture.md`

## Deployment topology

Both projects on one Contabo VPS. DBRealtorWeb joins DBRealtor's Docker Compose network to reach the `db` container.

```
Contabo VPS
├── /opt/DBRealtor/         docker-compose.prod.yml → [scraper, db]
└── /opt/DBRealtorWeb/      docker-compose.prod.yml → [portal-backend, portal-nginx]
                             connects to: dbrealtor_default network
```

## Related pages

- `scraper.md` — scraper internals
- `web.md` — web portal internals
- `../runbooks/deploy-scraper.md` — how to deploy the scraper
- `../runbooks/deploy-web.md` — how to deploy the portal
