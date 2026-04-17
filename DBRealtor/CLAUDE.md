# Sreality scraper — project context
 
## What this project is
A complete rewrite of a 7-year-old Python/MySQL web scraper for sreality.cz (Czech real estate portal).
Goal: collect, store, and analyse real estate listing data over time for personal market analysis.
 
## Project goals (in priority order)
1. Reliable, resumable scraping of sreality.cz listings
2. Clean historical data storage with change tracking (price changes, status changes)
3. Simple analysis layer: price trends, area comparisons, alerting on new listings
4. Low operational overhead — runs unattended, recovers from failures on its own
 
## Repository layout
See @docs/architecture.md for the full module breakdown.
See @docs/decisions.md for all architectural decisions and their rationale.
See @docs/progress.md for current build status and what's next.
 
## Stack (decided)
- Python 3.12+
- PostgreSQL (replaces old MySQL)
- Playwright or httpx+parsel for scraping (TBD in Phase 2)
- Docker + docker-compose for local and prod
- Task scheduling: APScheduler or cron (TBD)
 
## Hard rules
- Never commit secrets or API keys — use .env files, always in .gitignore
- All database changes go through migration files (Alembic), never raw ALTER TABLE
- Every scraping function must handle HTTP errors, timeouts, and rate limits gracefully
- Deduplication is mandatory: never insert a duplicate listing, always upsert
- Keep scraping polite: respect delays between requests, rotate user-agents
 
## Code style
- Python: Black formatter, isort, type hints on all public functions
- Docstrings on all modules and public classes
- Tests live in tests/ mirroring the src/ structure
- Use pytest, no unittest
 
## How to verify changes
```bash
docker compose up -d db        # start postgres
pytest tests/ -v               # run all tests
python -m src.scraper --dry-run  # scrape without writing to DB
```
 
## What NOT to do
- Don't add dependencies without checking docs/decisions.md first
- Don't rewrite the schema without creating an Alembic migration
- Don't use synchronous requests where async is available
- Don't ignore HTTP 429 responses — back off and retry