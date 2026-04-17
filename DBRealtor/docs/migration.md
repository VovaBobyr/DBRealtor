# Migration runbook — DigitalOcean → Contabo

This document is the authoritative step-by-step guide for migrating the
sreality scraper and all scraped data from the old DigitalOcean droplet to
a new Contabo Ubuntu server.

**Estimated total time:** 30–60 minutes depending on data volume and network speed.

---

## Overview

**Phase 1 — Prepare new Contabo server** (`scripts/setup_server.sh`)
- apt update/upgrade, Docker via official get.docker.com, git/curl/htop/ufw/fail2ban
- UFW: ports 22, 80, 443 open; fail2ban bans IPs after 5 failed SSH attempts
- Creates `/opt/sreality`, prints server IP, runs `docker run hello-world`

**Phase 2 — Backup on old DO server** (`scripts/backup_for_migration.sh`)
- Prints row counts before dumping (save these for Phase 4 verification)
- `pg_dump | gzip → backups/migration_YYYY-MM-DD.sql.gz`
- Prints the exact `scp` command to copy the file to the new server

**Phase 3 — Deploy on new server** (`scripts/deploy.sh`)
- Guards against missing `.env` — prints instructions and exits if absent
- `git pull → docker build → alembic upgrade head`
- Auto-restores the migration backup if `backups/migration_*.sql.gz` exists and the `listings` table is empty
- Prints listing count + last scrape run status at the end

**Phase 4 — Verify** (`scripts/verify_migration.sh`)
- Compares actual row counts against the values saved in Phase 2, with 1% tolerance
- Exits 0 on pass, 1 on fail
- Pass `--expected-listings N --expected-price-history N` for exact comparison

**Phase 5 — Cut over**
- Disable cron on old DO server first (prevent double-scraping)
- Set up identical crontab on new server (02:00 scrape, 06:00 backup)
- Trigger first scrape with `nohup`, monitor with `tail -f logs/cron.log | jq .`

**Phase 6 — Decommission**
- Cancel old DO droplet only after 2 successful scrape runs on the new server

### Key implementation notes

- `deploy.sh` restores the backup only when `listings` is empty — subsequent runs skip the restore silently
- `verify_migration.sh` `--expected-*` args are optional; if omitted it still queries and prints counts
- Restore streams directly: `gunzip -c | docker compose exec -T db psql` — no temp file on host

---

## Quick-reference checklist

- [ ] Phase 1 — Set up new Contabo server
- [ ] Phase 2 — Back up postgres on old DO server
- [ ] Phase 3 — Copy backup and deploy on new server
- [ ] Phase 4 — Verify migration data integrity
- [ ] Phase 5 — Set up cron, run first scrape, cut over
- [ ] Phase 6 — Decommission old server (after 2 successful scrape runs)

---

## Phase 1 — Prepare the new Contabo server

Run as **root** on the new Contabo server.

### 1.1 SSH in

```bash
ssh root@NEW_SERVER_IP
```

### 1.2 Run the setup script

The setup script installs Docker, configures UFW firewall, sets up fail2ban,
and creates `/opt/sreality`.

Option A — if you can clone the repo first:
```bash
# Under root
cd /opt
git clone https://github.com/VovaBobyr/DBRealtor.git sreality
chown -R deploy:deploy sreality/
cd sreality
bash scripts/setup_server.sh
# Under deploy
sudo groupadd docker # create docker group - may be already created
sudo usermod -aG docker deploy
newgrp docker
```

Option B — pipe directly from GitHub:
```bash
curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/master/scripts/setup_server.sh | bash
```

What the script does:
- `apt update && apt upgrade -y`
- Installs: git, curl, htop, ufw, fail2ban
- Installs Docker via the official get.docker.com script (not snap)
- Adds current user to the `docker` group
- Opens UFW ports: 22 (SSH), 80 (HTTP), 443 (HTTPS)
- Configures fail2ban to ban IPs after 5 failed SSH attempts
- Prints confirmation and runs `docker run hello-world`

### 1.3 Re-login to activate docker group membership

```bash
exit
ssh root@NEW_SERVER_IP
docker ps   # should return empty list, not "permission denied"
```

---

## Phase 2 — Back up postgres on the OLD DigitalOcean server

Run on the **old DO server**.

### 2.1 SSH in

```bash
ssh root@OLD_DO_IP
cd /opt/sreality
```

### 2.2 Run the migration backup script

```bash
bash scripts/backup_for_migration.sh
```

The script will:
1. Print row counts from the live DB (save these — you'll need them for Phase 4)
2. Run `pg_dump | gzip` to `/opt/sreality/backups/migration_YYYY-MM-DD.sql.gz`
3. Print the file size
4. Print the `scp` command to copy it to the new server

**Save the row counts printed by the script.** Example output to capture:
```
 tbl           | count
---------------+-------
 listings      |  4359
 price_history |  8821
 scrape_runs   |    12
```

### 2.3 Copy the backup to the new server

The script prints the exact command. It looks like:

```bash
scp /opt/sreality/backups/migration_2026-04-13.sql.gz root@NEW_SERVER_IP:/opt/sreality/backups/
```

Verify the file arrived:
```bash
ssh root@NEW_SERVER_IP ls -lh /opt/sreality/backups/
```

---

## Phase 3 — Deploy on the new Contabo server

Run on the **new Contabo server**.

### 3.1 Clone the repository (if not done in Phase 1)

```bash
mkdir -p /opt/sreality
cd /opt/sreality
git clone https://github.com/VovaBobyr/DBRealtor.git .
```

### 3.2 Create and populate .env

```bash
cp .env.example .env
```

Generate a strong password:
```bash
openssl rand -base64 16
```

Edit `.env`:
```bash
nano .env
```

Set these values (minimum required):
```
POSTGRES_PASSWORD=<strong-random-password>
DATABASE_URL=postgresql+asyncpg://sreality:<password>@db:5432/sreality
DATABASE_URL_SYNC=postgresql+psycopg2://sreality:<password>@db:5432/sreality
LOG_FORMAT=json
LOG_LEVEL=INFO
SCRAPE_DELAY_SECONDS=1.5
```

Use the **same password** in `POSTGRES_PASSWORD`, `DATABASE_URL`, and
`DATABASE_URL_SYNC`. The password must match in all three lines.

### 3.3 Run the deploy script

```bash
cd /opt/sreality
bash scripts/deploy.sh
```

`deploy.sh` will:
1. Pull the latest code
2. Build the Docker image
3. Start the postgres container
4. Wait for postgres to be ready
5. Run `alembic upgrade head` (creates all tables and enum types)
6. **Detect the migration backup** in `/opt/sreality/backups/migration_*.sql.gz`
7. If the `listings` table is empty, restore the backup automatically
8. Print the listing count and last scrape run status

The restore step may take several minutes for large dumps (4000+ listings).
You will see:
```
[deploy] Empty database detected. Restoring migration backup: .../migration_2026-04-13.sql.gz
[deploy] This may take several minutes for large dumps...
[deploy] Backup restored.
[deploy] Listings after restore: 4359
```

### 3.4 Verify the DB is up and tables exist

```bash
docker compose -f docker-compose.prod.yml exec db psql -U sreality -c "\dt"
```

Expected output: tables `listings`, `price_history`, `scrape_runs`.

---

## Phase 4 — Verify migration data integrity

Run on the **new Contabo server**.

### 4.1 Run the verification script with expected counts

Use the row counts saved in Phase 2.2:

```bash
cd /opt/sreality
bash scripts/verify_migration.sh \
    --expected-listings 4359 \
    --expected-price-history 8821
```

The script:
- Queries actual row counts from the new DB
- Compares against expected values with a 1% tolerance
- Prints PASS / FAIL per table
- Exits 0 if all pass, 1 if any fail

Example successful output:
```
[verify] Row counts on NEW server:
 table_name    | row_count
---------------+-----------
 listings      |      4359
 price_history |      8821
 scrape_runs   |        12

[verify] Active listings: 4312
[verify] Last 3 scrape runs: ...

[verify] Comparing against expected counts...
[verify] PASS  listings: actual=4359 expected=4359
[verify] PASS  price_history: actual=8821 expected=8821
[verify] RESULT: OK — all checks passed.
```

### 4.2 Manual spot-checks

```bash
docker compose -f docker-compose.prod.yml exec db psql -U sreality
```

```sql
-- Random sample of listings
SELECT sreality_id, title, price_czk, locality, first_seen_at
FROM listings ORDER BY RANDOM() LIMIT 5;

-- Price history for a listing
SELECT l.sreality_id, ph.price_czk, ph.recorded_at
FROM price_history ph
JOIN listings l ON l.id = ph.listing_id
ORDER BY ph.recorded_at DESC LIMIT 10;

-- Scrape run history
SELECT * FROM scrape_run_summary ORDER BY started_at DESC LIMIT 5;
\q
```

---

## Phase 5 — Cut over: cron, first scrape, DNS

### 5.1 Set up crontab on the new server

```bash
crontab -e
```

Add exactly these two lines (same schedule as the old server):
```cron
0 2 * * * /opt/sreality/scripts/run_nightly.sh >> /opt/sreality/logs/cron.log 2>&1
0 6 * * * /opt/sreality/scripts/backup_db.sh  >> /opt/sreality/logs/cron.log 2>&1
```

Verify:
```bash
crontab -l
```

### 5.2 Disable cron on the OLD server (prevent double-scraping)

SSH to the old DO server and remove or comment out the cron jobs:
```bash
crontab -e
# Comment out or delete the two lines
```

### 5.3 Trigger the first scrape on the new server

```bash
cd /opt/sreality
nohup bash scripts/run_nightly.sh >> logs/cron.log 2>&1 &
echo "Scraper PID: $!"
```

Monitor progress (each log line is JSON):
```bash
tail -f logs/cron.log | grep '^{' | jq .
```

Or watch raw output:
```bash
tail -f logs/cron.log
```

A full scrape of ~4000 listings takes approximately 3 hours at the default
`SCRAPE_DELAY_SECONDS=1.5`.

### 5.4 Verify the first scrape completed successfully

```bash
python scripts/healthcheck.py
```

Expected output:
```
OK       status=success  found=4300  new=0  updated=45  errors=0  age=1.2h
```

Or directly:
```bash
docker compose -f docker-compose.prod.yml exec db psql -U sreality -c "
SELECT status, listings_found, listings_new, listings_updated,
       EXTRACT(EPOCH FROM finished_at - started_at)::int AS duration_s,
       CASE WHEN jsonb_typeof(errors) = 'array'
            THEN jsonb_array_length(errors) ELSE 0 END AS error_count
FROM scrape_runs ORDER BY started_at DESC LIMIT 1;"
```

### 5.5 Run verify_migration.sh a second time after the first scrape

This confirms the scraper is writing to the new DB correctly:
```bash
bash scripts/verify_migration.sh
```

(No `--expected-*` args needed here — just checking that the DB is alive
and row counts are plausible.)

---

## Phase 6 — Decommission the old DigitalOcean server

**Do NOT cancel the old droplet until:**
- [ ] 2 successful nightly scrape runs have completed on the new server
- [ ] `python scripts/healthcheck.py` returns OK on the new server
- [ ] Cron jobs are confirmed running on the new server (`crontab -l`)
- [ ] You have at least one backup from the new server (`ls backups/`)

### 6.1 Final backup from the old server (optional safety net)

```bash
# On old DO server
bash scripts/backup_for_migration.sh
# Transfer to new server or local machine
```

### 6.2 Cancel the DigitalOcean droplet

1. Log in to DigitalOcean → Droplets
2. Select the old droplet → **Destroy Droplet**
3. Confirm with the droplet name

**This is irreversible.** The droplet and all its data are permanently deleted.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `deploy.sh` exits with `.env not found` | .env was not created | `cp .env.example .env && nano .env` |
| `deploy.sh` restore step skipped | DB already has rows | Truncate tables or use a fresh DB volume |
| `verify_migration.sh` FAIL on counts | Partial restore or network cut during scp | Re-run scp and re-run deploy.sh |
| Scraper exits with `Connection refused` | DB container not running | `docker compose -f docker-compose.prod.yml up -d db` |
| `alembic upgrade head` fails | Wrong `DATABASE_URL_SYNC` | Must use `psycopg2`, not `asyncpg`; check .env |
| 429 rate-limited by sreality | Delay too low | Set `SCRAPE_DELAY_SECONDS=2.0` in .env |
| fail2ban blocking your own IP | Too many failed logins | `fail2ban-client unban YOUR_IP` |
| UFW blocking docker networking | UFW + docker conflict | See: https://docs.docker.com/network/iptables/ |

### Re-running the restore manually

If deploy.sh skips the restore because the DB already has rows, restore manually:

```bash
cd /opt/sreality

# Drop all rows (careful — destructive)
docker compose -f docker-compose.prod.yml exec -T db psql -U sreality sreality -c \
    "TRUNCATE listings, price_history, scrape_runs RESTART IDENTITY CASCADE;"

# Then re-run deploy.sh — it will detect the empty DB and restore automatically
bash scripts/deploy.sh
```

Or restore directly without going through deploy.sh:
```bash
gunzip -c backups/migration_YYYY-MM-DD.sql.gz \
    | docker compose -f docker-compose.prod.yml exec -T db psql -U sreality sreality
```

---

## Day-to-day operations on new server

All commands are the same as documented in `docs/deployment.md` — just replace
the old server IP with the new Contabo IP. The application layout, scripts, and
crontab are identical.

```bash
# Check last scrape
python scripts/healthcheck.py

# View live logs
tail -f logs/cron.log | grep '^{' | jq .

# Manual scrape run
nohup bash scripts/run_nightly.sh >> logs/cron.log 2>&1 &

# Update application
bash scripts/deploy.sh

# List backups
ls -lh backups/
```

---

_Created: 2026-04-13 — Migration from DigitalOcean to Contabo._
