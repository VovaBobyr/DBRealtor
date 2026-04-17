# DBRealtor monorepo — context for Claude

## What this system is

A personal real estate market analysis platform for sreality.cz (Czech real estate portal).

```
sreality.cz → [DBRealtor scraper] → PostgreSQL ← [DBRealtorWeb portal]
```

- **DBRealtor** (`/DBRealtor/`) — Python scraper that runs nightly, stores listings + price history in PostgreSQL
- **DBRealtorWeb** (`/DBRealtorWeb/`) — Read-only analytics portal (FastAPI + React) over that same DB

## Knowledge base (wiki)

Before working on either subproject, check the relevant wiki pages:

- `wiki/architecture/overview.md` — full system diagram and data flow
- `wiki/architecture/scraper.md` — scraper internals (ADRs, schema, phases)
- `wiki/architecture/web.md` — web portal stack and API design
- `wiki/runbooks/deploy-scraper.md` — how to deploy DBRealtor to Contabo VPS
- `wiki/runbooks/deploy-web.md` — how to deploy DBRealtorWeb to Contabo VPS
- `wiki/prompts/` — reusable Claude prompt templates for this project

## Subproject CLAUDE.md files

Each subproject has its own CLAUDE.md with stack details, hard rules, and verification commands:
- `DBRealtor/CLAUDE.md` — scraper rules (Python, Alembic, httpx, no sync code)
- `DBRealtorWeb/CLAUDE.md` — portal rules (FastAPI read-only, TypeScript strict, TanStack Query)

## Server (Contabo VPS)

Both projects deploy to the same Contabo VPS. DBRealtorWeb connects to DBRealtor's PostgreSQL container via Docker network. Deploy scripts are:
- `DBRealtor/scripts/deploy.sh` — scraper deploy
- `DBRealtorWeb/deploy.sh` — portal deploy (finds scraper Docker network automatically)

## Hard rules that apply to both projects

- Never commit `.env` files — use `.env.example` only
- All DB schema changes go through Alembic migrations (DBRealtor owns the schema)
- DBRealtorWeb is strictly read-only — no INSERT/UPDATE/DELETE ever
- Both deploy scripts paths are stable — do not move or rename them (server cron/ssh expects these paths)

## GitHub (archived per-project history)

- Scraper: https://github.com/VovaBobyr/DBRealtor.git
- Portal: https://github.com/VovaBobyr/DBRealtorWeb.git
