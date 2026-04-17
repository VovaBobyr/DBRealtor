# Architecture

## Module layout

```
sreality-scraper/
├── CLAUDE.md
├── .env.example
├── .gitignore
├── docker-compose.yml
├── pyproject.toml
│
├── docs/
│   ├── architecture.md       ← this file
│   ├── decisions.md          ← ADRs and technology choices
│   └── progress.md           ← build checklist
│
├── src/
│   ├── scraper/
│   │   ├── __init__.py
│   │   ├── browser.py        ← Playwright/httpx session setup
│   │   ├── parser.py         ← HTML → structured listing dict
│   │   ├── paginator.py      ← handles multi-page search results
│   │   └── pipeline.py       ← orchestrates scrape → validate → store
│   │
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── models.py         ← SQLAlchemy ORM models
│   │   ├── repository.py     ← upsert, query, price history logic
│   │   └── session.py        ← DB session factory
│   │
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── queries.py        ← price trend, area stats SQL
│   │   └── alerts.py         ← new listing / price drop detection
│   │
│   └── scheduler/
│       ├── __init__.py
│       └── jobs.py           ← APScheduler job definitions
│
├── db/
│   └── migrations/           ← Alembic migration files
│       └── versions/
│
└── tests/
    ├── scraper/
    ├── storage/
    └── analysis/
```

## Database schema

### listings
| column | type | notes |
|---|---|---|
| id | uuid PK | |
| sreality_id | varchar(64) UNIQUE | source system ID |
| listing_type | enum | 'sale', 'rent' |
| property_type | enum | 'flat', 'house', 'land', 'commercial' |
| title | text | |
| description | text | |
| price_czk | bigint | current price in CZK |
| area_m2 | int | |
| floor | int | nullable |
| locality | text | city/district string from sreality |
| gps_lat | float | nullable |
| gps_lon | float | nullable |
| url | text | canonical listing URL |
| images | jsonb | list of image URLs |
| raw_data | jsonb | full scraped payload, for reprocessing |
| first_seen_at | timestamptz | |
| last_seen_at | timestamptz | updated every scrape run |
| is_active | bool | false = delisted |

### price_history
| column | type | notes |
|---|---|---|
| id | uuid PK | |
| listing_id | uuid FK → listings.id | |
| price_czk | bigint | |
| recorded_at | timestamptz | |

### scrape_runs
| column | type | notes |
|---|---|---|
| id | uuid PK | |
| started_at | timestamptz | |
| finished_at | timestamptz | nullable |
| listings_found | int | |
| listings_new | int | |
| listings_updated | int | |
| errors | jsonb | list of error strings |
| status | enum | 'running', 'success', 'failed' |

## Key data flows

### Scrape run
```
scheduler → pipeline.run_scrape()
  → paginator.get_all_pages()    # collect all listing URLs for search
  → parser.parse_listing(url)    # extract fields for each listing
  → repository.upsert_listing()  # insert or update, record price change
  → scrape_runs update           # mark finished
```

### Analysis query
```
analysis.queries.price_trend(locality, property_type, months=12)
  → returns list of (month, avg_price_czk, count)
```
