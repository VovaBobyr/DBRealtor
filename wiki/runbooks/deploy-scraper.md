# Runbook: Deploy DBRealtor Scraper

> Script: `/DBRealtor/scripts/deploy.sh`  
> Server path: `/opt/DBRealtor/`  
> Branch: `master` (GitHub: https://github.com/VovaBobyr/DBRealtor.git)

## What deploy.sh does (step by step)

1. Checks `.env` exists — creates from `.env.example` and **exits** if missing (forces manual password setup)
2. Parses `.env` safely (handles special characters in values like User-Agent strings)
3. `git pull --ff-only` — fast-forward only, never merges
4. `docker compose build scraper` — rebuilds image
5. `docker compose up -d db` — starts postgres, waits up to 60s for it to be ready
6. `docker compose run --rm scraper alembic upgrade head` — runs any pending migrations
7. If `backups/migration_*.sql.gz` exists AND listings table is empty → restores backup (first-time only)
8. Creates `logs/` and `backups/` directories
9. Runs `scripts/healthcheck.py` (non-fatal — normal on first deploy)
10. Prints listing count + last scrape run status

## First-time server setup

```bash
sudo apt update && sudo apt install -y docker.io docker-compose-plugin git
sudo usermod -aG docker $USER && newgrp docker

cd /opt
git clone https://github.com/VovaBobyr/DBRealtor.git
cd DBRealtor
cp .env.example .env
nano .env     # set POSTGRES_PASSWORD, DATABASE_URL, DATABASE_URL_SYNC
chmod +x scripts/deploy.sh
bash scripts/deploy.sh
```

## Subsequent deploys (from dev machine)

```bash
# 1. Push changes to GitHub from your dev machine
git push origin master

# 2. SSH to server and run
ssh user@SERVER_IP
cd /opt/DBRealtor
bash scripts/deploy.sh
```

## Crontab (nightly scrape)

```bash
crontab -e
# Add:
0 2 * * * cd /opt/DBRealtor && bash scripts/run_nightly.sh >> logs/cron.log 2>&1
```

## Useful commands on server

```bash
# Check scraper logs
docker compose -f docker-compose.prod.yml logs -f scraper

# Trigger manual scrape
docker compose -f docker-compose.prod.yml run --rm scraper python -m src.scraper

# Check DB health
docker compose -f docker-compose.prod.yml exec db psql -U sreality sreality \
  -c "SELECT COUNT(*) FROM listings WHERE is_active=true;"

# Run healthcheck
python scripts/healthcheck.py

# Create DB backup
bash scripts/backup_db.sh
```

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `deploy.sh` exits after `.env` check | No `.env` file | `cp .env.example .env && nano .env` |
| Postgres not ready after 60s | Docker daemon slow | `docker compose -f docker-compose.prod.yml up -d db` manually |
| Migration fails | Alembic version mismatch | Check `alembic current` vs `alembic heads` |
| Scraper exits immediately | CMP or network change | Check logs, update headers in `browser.py` |
| `UniqueViolationError` | Concurrent scraper processes | Kill extra processes, let one finish |

## .env required variables

```env
POSTGRES_PASSWORD=<strong-password>
POSTGRES_USER=sreality
POSTGRES_DB=sreality
DATABASE_URL=postgresql+asyncpg://sreality:<password>@db:5432/sreality
DATABASE_URL_SYNC=postgresql+psycopg2://sreality:<password>@db:5432/sreality
LOG_FORMAT=json
# Optional:
ALERT_EMAIL=you@example.com
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=...
SMTP_PASSWORD=...
```
