# Runbook: Deploy DBRealtorWeb Portal

> Script: `/DBRealtorWeb/deploy.sh`  
> Server path: `/opt/DBRealtorWeb/`  
> Branch: `main` (GitHub: https://github.com/VovaBobyr/DBRealtorWeb.git)  
> **Requires DBRealtor scraper already deployed** — shares its postgres container

## What deploy.sh does (step by step)

1. `git pull origin main`
2. Detects the scraper's Docker network: `docker network ls | grep -E 'dbrealtor|sreality'`
3. Exports `SCRAPER_NETWORK` env var
4. `docker compose -f docker-compose.prod.yml build`
5. `docker compose -f docker-compose.prod.yml up -d`
6. Health-checks `http://localhost/health` (retries 10×)
7. Prints server IP

## First-time server setup

```bash
# Prerequisite: DBRealtor must already be running (provides the db container)
cd /opt/DBRealtor && docker compose -f docker-compose.prod.yml ps  # db must be running

cd /opt
git clone https://github.com/VovaBobyr/DBRealtorWeb.git
cd DBRealtorWeb
cp .env.example .env
nano .env     # credentials MUST match DBRealtor/.env
chmod +x deploy.sh
bash deploy.sh
```

## .env required variables

```env
# Must match DBRealtor/.env exactly:
POSTGRES_USER=sreality
POSTGRES_PASSWORD=<same-as-scraper>
POSTGRES_DB=sreality

# db = service name inside scraper's compose network:
DATABASE_URL=postgresql+asyncpg://sreality:<password>@db:5432/sreality
```

## Subsequent deploys

```bash
# 1. Push changes to GitHub
git push origin main

# 2. SSH to server
ssh user@SERVER_IP
cd /opt/DBRealtorWeb
bash deploy.sh
```

## Production architecture

```
Browser → nginx :80
  /api/*    → proxy_pass → portal-backend :8000
  /health   → proxy_pass → portal-backend :8000
  /*        → serve /usr/share/nginx/html (pre-built React bundle)

portal-backend → db :5432 (scraper's postgres, via shared Docker network)
```

## Useful commands on server

```bash
# View logs
docker compose -f docker-compose.prod.yml logs -f

# Restart without rebuild
docker compose -f docker-compose.prod.yml up -d

# Rebuild + restart
docker compose -f docker-compose.prod.yml up -d --build

# Check health
curl http://localhost/health        # {"status":"ok"}
curl http://localhost/api/dashboard/summary | python3 -m json.tool
```

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `network not found` | Scraper compose not running | `cd /opt/DBRealtor && docker compose -f docker-compose.prod.yml up -d db` |
| `502 Bad Gateway` | Backend starting up | Wait 10s, retry; check `docker compose logs portal-backend` |
| Empty data | DB empty | Trigger scrape: `cd /opt/DBRealtor && bash scripts/run_nightly.sh` |
| Blank frontend page | Static build failed | `docker compose -f docker-compose.prod.yml build --no-cache` |
| Backend can't connect to DB | Wrong DATABASE_URL or password mismatch | Verify `.env` matches DBRealtor `.env` |
