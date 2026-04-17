# DBRealtorWeb Portal — Architecture

> Source: `/DBRealtorWeb/`  
> Full rules: `/DBRealtorWeb/CLAUDE.md`

## Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI (Python 3.12+), SQLAlchemy async, asyncpg |
| Frontend | React 18 + TypeScript + Vite |
| Styling | Tailwind CSS v3 |
| Charts | Recharts |
| HTTP client | TanStack Query (react-query) |
| Reverse proxy | Nginx |
| Containers | Docker + docker-compose |

## Key constraint: READ-ONLY

This project never writes to the database. No INSERT, UPDATE, or DELETE — ever.
All DB access via SQLAlchemy async sessions, no `session.commit()` or `session.add()`.

## Module structure

```
backend/src/
├── main.py           FastAPI app, CORS, router registration
├── database.py       async engine + get_session() dependency
├── models.py         read-only ORM mirrors of scraper schema
└── routers/
    ├── dashboard.py  summary stats
    ├── trends.py     price trend over time, new listings per day
    ├── listings.py   paginated listing table with filters
    └── alerts.py     new listings & price drops

frontend/src/
├── api/              TanStack Query hooks (one file per endpoint group)
├── components/       shared UI components
└── pages/
    ├── Dashboard.tsx
    ├── Trends.tsx
    ├── Listings.tsx
    └── Alerts.tsx
```

## Available API endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/api/dashboard/summary` | total listings, active count, last scrape |
| GET | `/api/trends/price` | avg price over time by property type |
| GET | `/api/trends/new-per-day` | new listings count per day |
| GET | `/api/listings` | paginated listing list with filters |
| GET | `/api/alerts/new` | listings added since N days |
| GET | `/api/alerts/price-drops` | listings with price decreases |

## Local development

```bash
cd DBRealtorWeb
cp .env.example .env   # fill in DB credentials matching DBRealtor/.env
docker compose up
# Frontend: http://localhost:5173
# Backend:  http://localhost:8000/docs
```
