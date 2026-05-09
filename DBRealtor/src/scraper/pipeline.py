"""Scrape pipeline — orchestrates paginator → parser → storage.

CLI usage:
    python -m src.scraper [--dry-run] [--url URL] [--limit N]

By default (no --url flag) the pipeline scrapes all cities in SEARCH_TARGETS
sequentially, with a 2-second pause between cities.
Pass --url to scrape a single search URL (useful for testing).
"""

import argparse
import asyncio
import os
import time
from datetime import datetime, timezone

import structlog

from src.alerts.email import send_failure_alert
from src.logging_config import configure_logging
from src.scraper.browser import make_client
from src.scraper.paginator import get_all_listing_ids
from src.scraper.parser import fetch_listing_detail
from src.storage.repository import (
    ScrapeRunData,
    close_scrape_run,
    mark_inactive,
    open_scrape_run,
    upsert_listing,
)
from src.storage.session import get_session

log = structlog.get_logger()

# ---------------------------------------------------------------------------
# Search targets — one entry per city / property-type combination.
# Add or remove cities here; the rest of the pipeline adjusts automatically.
# ---------------------------------------------------------------------------

SEARCH_TARGETS: list[dict[str, str]] = [
    {"city": "Praha",   "url": "https://www.sreality.cz/hledani/prodej/byty/praha"},
    {"city": "Praha",   "url": "https://www.sreality.cz/hledani/prodej/domy/praha"},
    {"city": "Brno",    "url": "https://www.sreality.cz/hledani/prodej/byty/brno"},
    {"city": "Brno",    "url": "https://www.sreality.cz/hledani/prodej/domy/brno"},
    {"city": "Ostrava", "url": "https://www.sreality.cz/hledani/prodej/byty/ostrava"},
    {"city": "Ostrava", "url": "https://www.sreality.cz/hledani/prodej/domy/ostrava"},
    {"city": "Plzeň",   "url": "https://www.sreality.cz/hledani/prodej/byty/plzen"},
    {"city": "Plzeň",   "url": "https://www.sreality.cz/hledani/prodej/domy/plzen"},
    {"city": "Liberec", "url": "https://www.sreality.cz/hledani/prodej/byty/liberec"},
    {"city": "Liberec", "url": "https://www.sreality.cz/hledani/prodej/domy/liberec"},
]

# Polite pause (seconds) between scraping different cities.
_INTER_CITY_PAUSE = 2


async def run_scrape(
    targets: list[dict[str, str]] | None = None,
    dry_run: bool = False,
    limit: int | None = None,
) -> None:
    """Run a full scrape cycle across all configured search targets.

    Args:
        targets:  List of {"city": ..., "url": ...} dicts. Defaults to
                  SEARCH_TARGETS (all configured cities).
        dry_run:  When True, parse and print without writing to DB.
        limit:    Cap on the number of listings to process *per city*
                  (useful for testing).
    """
    if targets is None:
        targets = SEARCH_TARGETS

    total_cities = len(targets)
    log.info("scrape_starting", dry_run=dry_run, cities=total_cities)

    all_ids: list[str] = []

    async with make_client() as client:
        for i, target in enumerate(targets, start=1):
            city = target["city"]
            url = target["url"]

            log.info("scraping_city", city=city, index=i, total=total_cities)
            print(f"Scraping {city} ({i}/{total_cities})...")

            city_ids = await get_all_listing_ids(client, url, max_ids=limit)
            log.info("city_ids_collected", city=city, count=len(city_ids))
            all_ids.extend(city_ids)

            if i < total_cities:
                log.debug("inter_city_pause", seconds=_INTER_CITY_PAUSE)
                await asyncio.sleep(_INTER_CITY_PAUSE)

        log.info("all_ids_collected", count=len(all_ids), cities=total_cities)

        if dry_run:
            await _run_dry(client, all_ids)
        else:
            await _run_with_db(client, all_ids)


async def _run_dry(client, all_ids: list[str]) -> None:
    """Fetch and print listings without touching the DB."""
    ok = 0
    skipped = 0
    for i, listing_id in enumerate(all_ids, start=1):
        listing = await fetch_listing_detail(client, listing_id)
        if listing is None:
            skipped += 1
            continue
        ok += 1
        print(
            f"[{i}/{len(all_ids)}] {listing.sreality_id:>12} | "
            f"{listing.listing_type:4} | {listing.property_type:10} | "
            f"{'N/A' if listing.price_czk is None else f'{listing.price_czk:,} CZK':>15} | "
            f"{listing.area_m2 or '?':>4} m² | "
            f"{listing.locality or '?'}"
        )
    log.info("dry_run_complete", parsed=ok, skipped=skipped)
    print(f"\nDry-run complete. Parsed {ok} listings, skipped {skipped}.")


async def _run_with_db(client, all_ids: list[str]) -> None:
    """Fetch listings and upsert them into the database."""
    run: ScrapeRunData | None = None
    errors: list[str] = []
    skipped = 0
    total = len(all_ids)

    try:
        async with get_session() as session:
            run = await open_scrape_run(session)

        # Bind scrape_run_id to context so every subsequent log line carries it.
        structlog.contextvars.bind_contextvars(scrape_run_id=str(run.id))
        log.info("scrape_run_started", run_id=str(run.id), total=total)

        loop_start = time.monotonic()
        for i, listing_id in enumerate(all_ids, start=1):
            log.debug("fetching_detail", index=i, total=total, listing_id=listing_id)
            listing = await fetch_listing_detail(client, listing_id)
            run.listings_found += 1

            if listing is None:
                skipped += 1
                errors.append(f"Failed to parse listing {listing_id}")
            else:
                async with get_session() as session:
                    status, _ = await upsert_listing(session, listing)

                if status == "new":
                    run.listings_new += 1
                elif status == "updated":
                    run.listings_updated += 1

                log.debug("listing_upserted", listing_id=listing_id, status=status)

            if i % 50 == 0 or i == total:
                elapsed = time.monotonic() - loop_start
                rate = i / elapsed if elapsed > 0 else 0
                eta_s = int((total - i) / rate) if rate > 0 else 0
                log.info(
                    "scrape_progress",
                    done=i,
                    total=total,
                    pct=round(i / total * 100, 1),
                    new=run.listings_new,
                    updated=run.listings_updated,
                    skipped=skipped,
                    errors=len(errors),
                    elapsed_s=int(elapsed),
                    eta_s=eta_s,
                )

        # Mark listings not seen in this run as inactive
        async with get_session() as session:
            inactive_count = await mark_inactive(session, active_sreality_ids=all_ids)
        if inactive_count:
            log.info("listings_marked_inactive", count=inactive_count)

        run.errors = errors

        async with get_session() as session:
            await close_scrape_run(session, run, status="success")

        log.info(
            "scrape_complete",
            run_id=str(run.id),
            found=run.listings_found,
            new=run.listings_new,
            updated=run.listings_updated,
            skipped=skipped,
            inactive=inactive_count,
            errors=len(errors),
        )

    except Exception as exc:
        log.exception("scrape_failed", error=str(exc))
        if run is not None:
            run.errors = errors + [str(exc)]
            _append_failed_run_log(run)
            send_failure_alert(run_id=str(run.id), error_summary=str(exc))
            try:
                async with get_session() as session:
                    await close_scrape_run(session, run, status="failed")
            except Exception:
                log.exception("could_not_save_failed_run")
        raise


def _append_failed_run_log(run: ScrapeRunData) -> None:
    """Append one line to logs/failed_runs.log for post-mortem inspection."""
    os.makedirs("logs", exist_ok=True)
    first_error = run.errors[0] if run.errors else "unknown"
    line = (
        f"{datetime.now(timezone.utc).isoformat()}  "
        f"run_id={run.id}  "
        f"found={run.listings_found}  "
        f"errors={len(run.errors)}  "
        f'first_error="{first_error[:120]}"\n'
    )
    with open("logs/failed_runs.log", "a") as fh:
        fh.write(line)


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Sreality scraper",
        prog="python -m src.scraper",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Parse and print without writing to DB",
    )
    p.add_argument(
        "--url",
        default=None,
        metavar="URL",
        help="Scrape a single search URL instead of all configured cities",
    )
    p.add_argument(
        "--limit",
        type=int,
        default=None,
        metavar="N",
        help="Stop after N listings per city (useful for testing)",
    )
    p.add_argument(
        "--log-level",
        default=os.getenv("LOG_LEVEL", "INFO"),
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level (default: INFO or $LOG_LEVEL)",
    )
    return p


def main() -> None:
    args = _build_parser().parse_args()
    configure_logging(level=args.log_level)

    # --url overrides the default multi-city targets for single-URL testing.
    targets = None
    if args.url:
        targets = [{"city": args.url, "url": args.url}]

    asyncio.run(run_scrape(targets=targets, dry_run=args.dry_run, limit=args.limit))


if __name__ == "__main__":
    main()
