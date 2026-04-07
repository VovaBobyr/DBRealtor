# Kickoff prompt — paste this as your first message to Claude Code

---

We are starting a full rewrite of a Python/MySQL web scraper for sreality.cz (Czech real estate portal). The project is described in CLAUDE.md and the docs/ folder.

Before writing any code, I need you to do the following:

1. **Read** CLAUDE.md, docs/architecture.md, and docs/decisions.md in full.

2. **Scaffold the project structure** exactly as defined in docs/architecture.md:
   - Create all directories and empty __init__.py files
   - Create a pyproject.toml with the dependencies listed in docs/decisions.md
   - Create a docker-compose.yml with postgres and the app service
   - Create a .env.example with all required environment variables (no real values)
   - Create a .gitignore appropriate for a Python/Docker project

3. **Set up Alembic** for database migrations:
   - Initialize alembic in the db/ directory
   - Create the first migration file for the initial schema (listings, price_history, scrape_runs tables)
   - The schema is described in docs/architecture.md

4. After scaffolding, **run a checklist**:
   - [ ] pyproject.toml parseable and dependencies make sense
   - [ ] docker-compose.yml starts cleanly
   - [ ] alembic upgrade head applies the migration without errors
   - [ ] pytest discovers tests/ without import errors

5. Once the scaffold is verified, **update docs/progress.md** to mark Phase 3 (scaffold) complete and list what's ready to build next.

Do not start implementing scraping logic yet. Scaffold and verify first.

---
