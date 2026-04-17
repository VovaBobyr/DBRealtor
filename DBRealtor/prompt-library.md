# Prompt library — Claude Code sessions

Paste the relevant prompt at the start of each new session.
Always start by referencing the docs so the agent has context.

---

## Session: Phase 2 — Inspect sreality.cz and decide scraping approach

```
Read CLAUDE.md, docs/decisions.md, and docs/progress.md first.

I need you to investigate sreality.cz to resolve ADR-002 (scraping library choice):

1. Use httpx to fetch a sreality.cz search results page (e.g. https://www.sreality.cz/hledani/prodej/byty/praha)
2. Check whether listing data is in the HTML response or loaded via XHR
3. If XHR: find the JSON API endpoint and document its structure in docs/decisions.md
4. If server-side HTML: confirm parsel/CSS selectors can extract listing cards
5. Document your finding and update ADR-002 with the decision + rationale
6. Update docs/progress.md Phase 2 checklist

Do not start building yet — investigate and document first.
```

---

## Session: Phase 4a — Build the scraper

```
Read CLAUDE.md, docs/architecture.md, docs/decisions.md, docs/progress.md.

Build the scraper layer (src/scraper/). Work through it in this order:
1. browser.py — httpx async session with headers, retries, rate limiting
2. paginator.py — takes a search URL, yields all listing URLs across pages
3. parser.py — takes a listing URL/response, returns a validated Pydantic model
4. Add --dry-run CLI flag to pipeline.py that scrapes but does not write to DB

Write tests as you go in tests/scraper/:
- test_parser.py: use saved HTML fixtures, no network calls
- test_paginator.py: mock httpx, test pagination logic

After each file, run pytest tests/scraper/ -v and fix any failures before moving on.
Update docs/progress.md when done.
```

---

## Session: Phase 4b — Storage and pipeline

```
Read CLAUDE.md, docs/architecture.md, docs/progress.md.

Build the storage layer (src/storage/) and wire up pipeline.py:
1. models.py — SQLAlchemy 2.x models for listings, price_history, scrape_runs
2. repository.py — upsert_listing() that detects price changes and inserts price_history rows
3. session.py — async session factory using asyncpg
4. pipeline.py — full scrape → validate → upsert → log run flow

Integration test requirements:
- tests/storage/test_repository.py must run against a real postgres instance
- Use docker compose up -d db to start postgres before running tests
- Seed test data, upsert the same listing twice with a different price, assert price_history has 2 rows

Update docs/progress.md when done.
```

---

## Session: Phase 6 — Data migration from old MySQL

```
Read CLAUDE.md, docs/architecture.md, docs/progress.md.

I have a MySQL dump from the old project at: [PATH TO DUMP FILE]
The old schema has these tables: [DESCRIBE OLD TABLES HERE]

Write a migration script at scripts/migrate_from_mysql.py that:
1. Reads the MySQL dump (or connects to old MySQL if running)
2. Maps old fields to new schema — document any field that doesn't map cleanly
3. Inserts into new postgres DB using repository.upsert_listing()
4. Prints a summary: rows read, rows inserted, rows skipped (duplicates), errors

After running, validate:
- SELECT COUNT(*) FROM listings matches old row count (approximately)
- Spot-check 5 listings: compare old and new records side by side
- Check price_history was populated where old data has price change records

Update docs/progress.md when done.
```

---

## Session: Generic — continue from last session

```
Read CLAUDE.md and docs/progress.md.
Summarise what is complete and what is next according to the checklist.
Then continue with the next unchecked item.
Ask me before starting any task that would modify the database schema.
```

---

## Useful one-liners to use mid-session

Ask the agent to checkpoint:
> "Before continuing, update docs/progress.md with what we've done so far."

Ask the agent to explain a decision:
> "Before implementing this, explain your approach and wait for my OK."

Reset context cleanly:
> Use /clear in Claude Code, then paste the relevant session prompt above.

Ask the agent to review its own work:
> "Review what you just wrote. Check for: missing error handling, missing type hints, any place a duplicate listing could slip through."
```
