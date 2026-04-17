# Architecture decisions

This file records all major technology and design choices.
Update this file before adding new dependencies or changing patterns.

---

## ADR-001 — PostgreSQL over MySQL
**Decision:** Migrate from MySQL to PostgreSQL.
**Reason:** JSONB columns for raw_data/images storage, better support for window functions needed in price trend analysis, TimescaleDB extension available if time-series queries become complex. No meaningful operational difference for a single-user project.

---

## ADR-002 — Scraping library
**Status:** DECIDED — httpx + json (no Playwright needed).
**Decision:** Use `httpx` for HTTP and Python's built-in `json` to parse `__NEXT_DATA__`. Drop `parsel` and `playwright` from the active scraping path.

### Investigation findings (2026-04-06)

sreality.cz is a **Next.js SSR application**. Every page response (search and detail) embeds the full listing data as JSON inside a `<script id="__NEXT_DATA__" type="application/json">` tag. No JavaScript execution is required.

**Access method:** plain `httpx.get()` with a browser `User-Agent` header and a cookie to bypass the CMP consent wall (`szncmpone=1`). The response is 200 with a full HTML body (~700KB) containing all data.

**Search results page** (`/hledani/prodej/byty/LOCALITY?strana=PAGE`):
- JSON path: `props.pageProps.dehydratedState.queries[4].state.data`
- `.results` — list of 20–22 listing summaries
- `.pagination` — `{ limit, offset, total, totalWithPromo }`
- Fields per listing: `id`, `name`, `categoryMainCb`, `categorySubCb`, `categoryTypeCb`, `locality` (city, district, lat, lon), `priceCzk`, `priceCzkPerSqM`, `images`

**Detail page** (`/detail/TYPESEO/CATEGORYSEO/LOCALITYSEO/ID`):
- JSON path: same `queries[N].state.data` where queryKey `[0] == 'estate'`
- Adds: `description`, `params.usableArea` (m²), `params.floorNumber`, `params.floorArea`, full locality, `params.buildingCondition`, `params.ownership`, and ~60 more property attributes

**Field mapping to DB schema:**

| DB column | Source field |
|---|---|
| `sreality_id` | `id` (int, e.g. `1399477068`) |
| `listing_type` | `categoryTypeCb.value` — 1=sale, 2=rent |
| `property_type` | `categoryMainCb.value` — 1=flat, 2=house, 3=land, 4=commercial |
| `title` | `name` |
| `description` | `description` (detail page only) |
| `price_czk` | `priceCzk` |
| `area_m2` | `params.usableArea` (detail page only) |
| `floor` | `params.floorNumber` (detail page only) |
| `locality` | `"{locality.city}, {locality.district}"` |
| `gps_lat` | `locality.latitude` |
| `gps_lon` | `locality.longitude` |
| `url` | final redirect URL after fetching detail page |
| `images` | `images` array (`[{url, restbType, order}]`) |
| `raw_data` | full `estate` dict from detail page |

**Scrape strategy:**
1. Paginate search results pages (`strana=1..N`) to collect all listing IDs.
2. For each ID, fetch the detail page to get full data.
3. The detail URL can be any path ending in `/{id}` — sreality redirects to the canonical URL. Use `https://www.sreality.cz/detail/x/x/x/{id}` as a stable shortcut.

**Why not Playwright:** JS execution is not needed. The SSR data is complete in the raw HTML.
**Why not parsel:** Data is JSON, not HTML-fragmented. `json.loads()` on the `__NEXT_DATA__` script tag content is simpler and more stable than CSS/XPath selectors.

---

## ADR-003 — SQLAlchemy 2.x ORM
**Decision:** Use SQLAlchemy 2.x with async support (asyncpg driver).
**Reason:** Type-safe queries, Alembic migration support, familiar Python ecosystem.
**Dependencies:** `sqlalchemy[asyncio]`, `asyncpg`, `alembic`

---

## ADR-004 — APScheduler for scheduling
**Decision:** APScheduler 3.x with AsyncIOScheduler.
**Reason:** Keeps scheduling in-process, no external dependency (no Celery/Redis needed for a single-machine project). Can be swapped for a cron job in a container if needed.

---

## ADR-005 — Docker Compose for local + production
**Decision:** Single docker-compose.yml with profiles for dev and prod.
**Reason:** Reproducible environment, easy postgres setup, consistent between local and VPS.

---

## ADR-006 — CMP consent-wall bypass method
**Decision:** Send `Accept: application/json` and `X-Requested-With: XMLHttpRequest` headers on every request.
**Status:** DECIDED — discovered during Phase 4a smoke testing (2026-04-06).

**Background:** sreality.cz uses the Seznam CMP (Consent Management Platform). Requests without valid consent cookies are redirected through `bcr.iva.seznam.cz` → `cmp.seznam.cz/nastaveni-souhlasu`, which serves the cookie-consent page instead of the real content.

**What no longer works:** Setting `Cookie: szncmpone=1` (or `euconsent-v2=accept; szncmp=1`) was sufficient during the Phase 2 investigation but failed by Phase 4a — the BCR token validation became stricter and requires a properly signed IAB TCF v2 consent string, not a plain value.

**Fix:** The Next.js server skips the CMP redirect entirely when the request looks like an XHR/API call:
```python
"Accept": "application/json, text/plain, */*",
"X-Requested-With": "XMLHttpRequest",
```
The HTML response is identical (same `__NEXT_DATA__` content) — the headers only affect the redirect routing, not the server-side rendering.

**Fragility note:** This relies on server-side logic that distinguishes XHR from browser navigation. If sreality adds CMP enforcement for XHR requests, the fallback is to POST to `cmp.seznam.cz` to accept consent and extract the resulting cookies.

---

## ADR-007 — Detail page URL shortcut
**Decision:** Use `/detail/prodej/byt/1+kk/x/{id}` as the canonical shortcut for fetching any listing detail page.
**Status:** DECIDED — discovered during Phase 4a smoke testing (2026-04-06).

**Background:** sreality.cz detail URLs follow the pattern `/detail/{type}/{category}/{subcategory}/{locality}/{id}`. The full canonical form requires knowing locality, subcategory, and type — information not available until after the detail page is fetched.

**What does not work:** `/detail/x/x/x/{id}` returns 404. Only the first three path segments must be valid sreality identifiers; "x" is rejected for those positions.

**Fix:** Use `/detail/prodej/byt/1+kk/x/{id}`. sreality matches listings by numeric ID and issues a 301 redirect to the canonical URL regardless of the type/category/subcategory prefix. The locality segment (4th position) can be `x` — it is ignored. Verified across flat, house, land, and commercial listings.

**Implication:** The `url` field stored in the DB comes from `str(response.url)` after following the redirect — always the canonical form.

---

## Dependency list (pyproject.toml)
```toml
[project]
name = "sreality-scraper"
requires-python = ">=3.12"

dependencies = [
    "sqlalchemy[asyncio]>=2.0",
    "asyncpg>=0.29",
    "alembic>=1.13",
    "httpx>=0.27",
    "parsel>=1.9",
    "playwright>=1.44",       # install only if ADR-002 resolves to Playwright
    "apscheduler>=3.10",
    "pydantic>=2.0",           # for data validation of scraped fields
    "python-dotenv>=1.0",
    "structlog>=24.0",         # structured logging
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.23",
    "pytest-mock>=3.12",
    "black>=24.0",
    "isort>=5.13",
    "mypy>=1.9",
]
```
