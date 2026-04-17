# Deployment guide — DigitalOcean

Target: single Ubuntu 24.04 Droplet, $12/month (2 vCPU, 2 GB RAM), Docker.

---

## 1. Create the Droplet

1. Log in to DigitalOcean → **Create → Droplet**
2. Image: **Ubuntu 24.04 LTS**
3. Plan: **Basic → Regular → $12/month** (2 vCPU / 2 GB)
4. Datacenter: Frankfurt or Amsterdam (low latency to sreality.cz CZ servers)
5. Authentication: **SSH key** (paste your public key)
6. Hostname: `sreality-scraper` (or any name)
7. Click **Create Droplet** — note the IP address

---

## 2. Initial server setup

```bash
# From your local machine
ssh root@<DROPLET_IP>
```

```bash
# On the server — create a non-root user (optional but recommended)
adduser deploy
usermod -aG sudo deploy
rsync --archive --chown=deploy:deploy ~/.ssh /home/deploy/
su - deploy
```

### Install Docker

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker          # apply without re-login
docker --version       # verify
```

---

## 3. Clone the repository

```bash
sudo mkdir -p /opt/sreality
sudo chown $USER:$USER /opt/sreality
cd /opt
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git sreality
cd sreality
```

---

## 4. Create the .env file

```bash
cp .env.example .env
# Generate password
openssl rand -base64 16
# Inster this password in 3 lines in .env:
nano .env
```

Set at minimum:

```
POSTGRES_PASSWORD=<strong-random-password>
DATABASE_URL=postgresql+asyncpg://sreality:<password>@db:5432/sreality
DATABASE_URL_SYNC=postgresql+psycopg2://sreality:<password>@db:5432/sreality
LOG_FORMAT=json
LOG_LEVEL=INFO
SCRAPE_DELAY_SECONDS=1.5
```

Optionally set `ALERT_EMAIL`, `SMTP_HOST`, etc. for failure alerts.

**Never commit `.env` to git — it is in `.gitignore`.**

---

## 5. First deploy

```bash
cd /opt/sreality
bash scripts/deploy.sh
```

This will:
- Build the Docker image
- Start the postgres container
- Run `alembic upgrade head` (creates tables)
- Print "Deploy complete"

Verify the DB is up:

```bash
docker compose -f docker-compose.prod.yml exec db \
    psql -U sreality -c "\dt"
```

Expected output: tables `listings`, `price_history`, `scrape_runs`.

---

## 6. Set up cron and run the first scrape

Set up the nightly schedule first — this way the first scrape and all future scrapes
run unattended, and closing your SSH session won't interrupt anything.

```bash
crontab -e
```

Add these two lines:

```cron
0 2 * * * /opt/sreality/scripts/run_nightly.sh >> /opt/sreality/logs/cron.log 2>&1
0 6 * * * /opt/sreality/scripts/backup_db.sh  >> /opt/sreality/logs/cron.log 2>&1
```

- Scrape runs at **02:00 UTC** nightly (~3 hours for ~4000 listings)
- Backup runs at **06:00 UTC** — 1-hour buffer after scrape finishes

Verify cron is registered:

```bash
crontab -l
```

Then trigger the **first scrape immediately**, detached from your terminal:

```bash
nohup bash /opt/sreality/scripts/run_nightly.sh >> /opt/sreality/logs/cron.log 2>&1 &
echo "Scraper PID: $!"
```

You can safely close the SSH session. Reconnect any time and check progress:

```bash
tail -f /opt/sreality/logs/cron.log | jq .
```

When complete, verify the result:

```bash
docker compose -f docker-compose.prod.yml exec db psql -U sreality -c "
SELECT status, listings_found, listings_new, listings_updated,
       EXTRACT(EPOCH FROM finished_at - started_at)::int AS duration_s,
       CASE WHEN jsonb_typeof(errors) = 'array'
            THEN jsonb_array_length(errors) ELSE 0 END AS error_count
FROM scrape_runs ORDER BY started_at DESC LIMIT 1;"
```

---

## 7. Day-to-day operations

### Check the last scrape run

```bash
python scripts/healthcheck.py
```

Or directly:

```bash
docker compose -f docker-compose.prod.yml exec db psql -U sreality \
    -c "SELECT * FROM scrape_run_summary ORDER BY started_at DESC LIMIT 3;"
```

### View live scraper logs

```bash
# All output goes to cron.log — JSON lines from structlog, plain lines from bash wrappers
tail -f logs/cron.log | grep '^{' | jq .   # JSON log lines only (structlog)
tail -f logs/cron.log                        # everything including bash wrapper lines
```

### Check for failures

```bash
cat logs/failed_runs.log        # one line per failed run
cat logs/cron.log | grep FAIL   # cron-level failures
```

### List backups

```bash
ls -lh backups/
```

---

## 8. Updating the application

```bash
cd /opt/sreality
bash scripts/deploy.sh
```

`deploy.sh` runs `git pull`, rebuilds the image, and runs any new migrations.
The running database is untouched — only the image is rebuilt.

---

## 9. Firewall (optional, recommended)

```bash
sudo ufw allow OpenSSH
sudo ufw enable
sudo ufw status
```

Postgres is not exposed on any public port (no `ports:` in docker-compose.prod.yml),
so no additional firewall rule is needed for it.

---

## Troubleshooting

| Symptom | Check |
|---|---|
| Scraper exits immediately with DB error | `docker compose -f docker-compose.prod.yml logs db` — is postgres healthy? |
| `alembic upgrade head` fails | Check `DATABASE_URL_SYNC` in `.env` — must use `psycopg2`, not `asyncpg` |
| 429 rate-limited by sreality | Increase `SCRAPE_DELAY_SECONDS` in `.env` (try 2.0 or 3.0) |
| Backup file is 0 bytes | Postgres container not running — start with `deploy.sh` |
| Healthcheck shows STALE | Scraper running > 3h — check `logs/cron.log` for hangs |
