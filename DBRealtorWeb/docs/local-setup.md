# Local development setup — DBRealtorWeb

The portal is **read-only** over the DBRealtor scraper's PostgreSQL. You cannot
run it in isolation — you need the scraper's database populated (or at least
migrated) first.

Recommended dev flow: scraper's Postgres in Docker, portal backend + frontend
running natively on the host for hot reload.

## Prerequisites

- Python 3.12+
- Node.js 22+ and npm
- Docker + Docker Compose
- Git

## 1. Start the scraper's Postgres

The portal talks to the same database the scraper writes to. Follow
`DBRealtor/docs/local-setup.md` steps 1–5 first. At minimum:

```bash
cd DBRealtor
cp .env.example .env            # if not already done
docker compose up -d db
alembic upgrade head            # creates listings / price_history / scrape_runs
```

Optional — seed a bit of real data so the charts have something to render:

```bash
python -m src.scraper --limit 50
```

Postgres is now on `localhost:5432` with the schema the portal expects.

## 2. Configure the portal

```bash
cd ../DBRealtorWeb
cp .env.example .env
```

The `.env.example` assumes Docker internal networking (`@db:5432`). For **native
dev** against the scraper's host-exposed Postgres, change `DATABASE_URL` to
point at `localhost`:

```dotenv
DATABASE_URL=postgresql+asyncpg://sreality:changeme@localhost:5432/sreality
```

Keep user / password / db name in sync with the scraper's `.env`.

## 3. Backend (FastAPI on :8000)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

# Load .env from the project root and run uvicorn
export $(grep -v '^#' ../.env | xargs)   # Windows PowerShell: see note below
uvicorn src.main:app --reload --port 8000
```

Windows PowerShell — load the `.env` with:

```powershell
Get-Content ..\.env | Where-Object { $_ -notmatch '^\s*#' -and $_ -match '=' } |
  ForEach-Object { $kv = $_ -split '=', 2; [Environment]::SetEnvironmentVariable($kv[0].Trim(), $kv[1].Trim(), 'Process') }
uvicorn src.main:app --reload --port 8000
```

Verify:

```bash
curl http://localhost:8000/health                      # {"status":"ok"}
curl http://localhost:8000/api/dashboard/summary       # JSON payload
```

API docs: <http://localhost:8000/docs>.

## 4. Frontend (Vite on :5173)

```bash
cd ../frontend
npm install
npm run dev
```

Vite proxies `/api/*` to `http://localhost:8000` (see `vite.config.ts`), so no
`VITE_API_URL` is needed in dev.

Open <http://localhost:5173>. The Trends page should show both charts once the
DB has data.

## 5. Run the backend tests

Tests hit a real Postgres. `conftest.py` hard-exits if `DATABASE_URL` is not set.

```bash
cd backend
source .venv/bin/activate
export DATABASE_URL=postgresql+asyncpg://sreality:changeme@localhost:5432/sreality
pytest tests/ -v
```

The helper tests in `tests/test_trends_helpers.py` do not open a connection —
any non-empty `DATABASE_URL` is enough to get past the conftest check.

## Alternative: full-Docker dev

`docker compose up` from `DBRealtorWeb/` spins up its **own** Postgres, backend,
frontend, and nginx. That Postgres is empty and unrelated to the scraper's
data — fine for wiring checks, useless for real analytics work. The port
5432 mapping will also conflict if the scraper's `db` is already running on the
host. Stop one before starting the other, or edit the host port in one of the
compose files.

## Troubleshooting

| Problem | Fix |
|---|---|
| `DATABASE_URL environment variable is required for integration tests` | Export `DATABASE_URL` before `pytest` (step 5). |
| Backend starts but every `/api/*` returns 500 | `alembic upgrade head` in the scraper repo — tables are missing. |
| Trends / Dashboard pages are empty | DB has schema but no rows. Run `python -m src.scraper --limit 50` in the scraper repo. |
| `port 5432 already in use` when starting scraper's db | Another Postgres (often the portal's own compose db) is bound. Stop it or change the host port. |
| CORS error in browser console | You're hitting the backend on a port other than 5173. The allowlist in `src/main.py` is `5173`, `80`, `localhost`. |
| Vite dev server: `/api/...` returns HTML instead of JSON | Backend isn't running on :8000, or was started with a different port. Check step 3. |
