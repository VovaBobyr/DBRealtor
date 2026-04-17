# Local development setup

## Prerequisites

- Python 3.12+
- Docker + Docker Compose
- Git

## Steps

### 1. Clone and enter the repo

```bash
git clone <repo-url>
cd DBRealtor
```

### 2. Create virtual environment and install dependencies

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

### 3. Configure environment

```bash
cp .env.example .env
```

Defaults in `.env` work out of the box for local development. Change `POSTGRES_PASSWORD` if desired, but keep it consistent across all three `DATABASE_URL*` lines.

Set `LOG_FORMAT=pretty` for readable dev logs.

### 4. Start PostgreSQL

```bash
docker compose up -d db
```

Postgres is now available at `localhost:5432`.

### 5. Run migrations

```bash
alembic upgrade head
```

Creates `listings`, `price_history`, and `scrape_runs` tables.

### 6. Verify

```bash
pytest tests/ -v
```

All 44 tests should pass (no network calls, uses an in-memory test DB).

---

## Daily development

**Run a test scrape (no DB writes):**
```bash
python -m src.scraper --dry-run --limit 5
```

**Run a real scrape (writes to DB):**
```bash
python -m src.scraper --limit 20
```

**Run analysis CLI:**
```bash
python -m src.analysis price-trend --locality "Praha" --months 6
python -m src.analysis alerts
```

**Stop the DB:**
```bash
docker compose down
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `alembic upgrade head` fails with connection error | `docker compose up -d db` and wait ~5 s for healthcheck |
| `ModuleNotFoundError: src` | Activate venv and run `pip install -e .` |
| Scraper gets CMP redirect page | Ensure `Accept: application/json` + `X-Requested-With: XMLHttpRequest` headers are set (see ADR-006) |
