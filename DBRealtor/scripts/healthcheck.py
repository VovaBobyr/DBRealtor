#!/usr/bin/env python3
"""Health check: prints last scrape run status, exits 0 (ok) or 1 (problem).

Usage:
    python scripts/healthcheck.py
    python scripts/healthcheck.py --max-age-hours 25
"""
import argparse
import asyncio
import os
import sys
from datetime import datetime, timezone

from dotenv import load_dotenv

load_dotenv()

_MAX_AGE_HOURS_DEFAULT = 25  # alert if last SUCCESS is older than this
_MAX_RUNNING_HOURS = 3       # flag as stale if still "running" beyond this


async def check(max_age_hours: int) -> int:
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import create_async_engine

    engine = create_async_engine(os.environ["DATABASE_URL"])
    async with engine.connect() as conn:
        row = (
            await conn.execute(
                text("""
                    SELECT id, status, started_at, finished_at,
                           listings_found, listings_new, listings_updated,
                           CASE WHEN jsonb_typeof(errors) = 'array'
                                THEN jsonb_array_length(errors) ELSE 0 END AS error_count
                    FROM scrape_runs
                    ORDER BY started_at DESC LIMIT 1
                """)
            )
        ).one_or_none()
    await engine.dispose()

    if row is None:
        print("UNKNOWN  no scrape runs in database")
        return 1

    age_h = (datetime.now(timezone.utc) - row.started_at).total_seconds() / 3600
    summary = (
        f"status={row.status}  "
        f"found={row.listings_found}  new={row.listings_new}  "
        f"updated={row.listings_updated}  errors={row.error_count}  "
        f"age={age_h:.1f}h"
    )

    if row.status == "success" and age_h <= max_age_hours:
        print(f"OK       {summary}")
        return 0

    if row.status == "running":
        if age_h < _MAX_RUNNING_HOURS:
            print(f"RUNNING  {summary}")
            return 0
        print(f"STALE    {summary}  (running for {age_h:.1f}h — possible hang)")
        return 1

    print(f"FAIL     {summary}")
    return 1


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--max-age-hours",
        type=int,
        default=_MAX_AGE_HOURS_DEFAULT,
        help=f"Alert if last successful run is older than this (default: {_MAX_AGE_HOURS_DEFAULT}h)",
    )
    args = p.parse_args()
    sys.exit(asyncio.run(check(args.max_age_hours)))


if __name__ == "__main__":
    main()
