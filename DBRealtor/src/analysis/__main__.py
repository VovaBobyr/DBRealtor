"""CLI for the analysis layer.

Commands:
    price-trend  Monthly avg price for a locality + property type.
    area-stats   Per-locality price/area summary for a property type.
    recent       Listings first seen within the last N hours.
    alerts       New listings and price drops since N hours ago.

Usage examples:
    python -m src.analysis price-trend --locality Praha --property-type flat
    python -m src.analysis area-stats --property-type house --min-listings 2
    python -m src.analysis recent --hours 48 --listing-type sale
    python -m src.analysis alerts --hours 24 --min-drop 5
"""

import argparse
import asyncio
import sys
from datetime import datetime, timedelta, timezone

from src.analysis.alerts import new_listings_since, price_drops_since
from src.analysis.queries import area_stats, price_trend, recent_listings
from src.storage.session import get_session


# ---------------------------------------------------------------------------
# Formatters
# ---------------------------------------------------------------------------


def _fmt_price(czk: int | None) -> str:
    if czk is None:
        return "N/A"
    return f"{czk:,} CZK"


# ---------------------------------------------------------------------------
# Sub-command handlers
# ---------------------------------------------------------------------------


async def cmd_price_trend(args: argparse.Namespace) -> None:
    async with get_session() as session:
        points = await price_trend(
            session,
            locality=args.locality,
            property_type=args.property_type,
            months=args.months,
        )

    if not points:
        print("No data found.")
        return

    print(f"\nPrice trend — {args.locality} / {args.property_type} (last {args.months} months)\n")
    print(f"{'Month':<10}  {'Avg price':>15}  {'Count':>6}")
    print("-" * 36)
    for p in points:
        print(f"{p.month:<10}  {_fmt_price(p.avg_price_czk):>15}  {p.count:>6}")


async def cmd_area_stats(args: argparse.Namespace) -> None:
    async with get_session() as session:
        stats = await area_stats(
            session,
            property_type=args.property_type,
            min_listings=args.min_listings,
        )

    if not stats:
        print("No data found.")
        return

    print(f"\nArea stats — {args.property_type} (min {args.min_listings} listings)\n")
    print(f"{'Locality':<35}  {'Avg price':>15}  {'Median m²':>10}  {'Count':>6}")
    print("-" * 72)
    for s in stats:
        med = f"{s.median_area_m2:.0f}" if s.median_area_m2 is not None else "N/A"
        print(
            f"{(s.locality or 'Unknown'):<35}  "
            f"{_fmt_price(s.avg_price_czk):>15}  "
            f"{med:>10}  "
            f"{s.listing_count:>6}"
        )


async def cmd_recent(args: argparse.Namespace) -> None:
    async with get_session() as session:
        listings = await recent_listings(
            session,
            since_hours=args.hours,
            listing_type=args.listing_type,
            property_type=args.property_type,
        )

    if not listings:
        print(f"No new listings in the last {args.hours} hours.")
        return

    print(f"\nListings first seen in the last {args.hours} hours ({len(listings)} total)\n")
    for listing in listings:
        print(
            f"  {listing.sreality_id:>12}  "
            f"{listing.listing_type:4} / {listing.property_type:<10}  "
            f"{_fmt_price(listing.price_czk):>15}  "
            f"{listing.area_m2 or '?':>4} m²  "
            f"{listing.locality or '?'}"
        )
        print(f"              {listing.url}")


async def cmd_alerts(args: argparse.Namespace) -> None:
    since = datetime.now(timezone.utc) - timedelta(hours=args.hours)

    async with get_session() as session:
        new = await new_listings_since(session, since)

    async with get_session() as session:
        drops = await price_drops_since(session, since, min_drop_pct=args.min_drop)

    print(f"\n=== Alerts for the last {args.hours} hours ===\n")

    print(f"New listings: {len(new)}")
    for listing in new:
        print(
            f"  [{listing.sreality_id}] {listing.title}  "
            f"{_fmt_price(listing.price_czk)}  {listing.locality or '?'}"
        )
        print(f"    {listing.url}")

    print(f"\nPrice drops >= {args.min_drop}%: {len(drops)}")
    for drop in drops:
        print(
            f"  [{drop.sreality_id}] {drop.title}  "
            f"{_fmt_price(drop.old_price_czk)} → {_fmt_price(drop.new_price_czk)}  "
            f"(-{drop.drop_pct:.1f}%)  {drop.locality or '?'}"
        )
        print(f"    {drop.url}")


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Sreality analysis CLI",
        prog="python -m src.analysis",
    )
    sub = p.add_subparsers(dest="command", required=True)

    # price-trend
    pt = sub.add_parser("price-trend", help="Monthly avg price trend")
    pt.add_argument("--locality", required=True, help="Locality substring to match")
    pt.add_argument(
        "--property-type",
        required=True,
        choices=["flat", "house", "land", "commercial"],
    )
    pt.add_argument("--months", type=int, default=12, metavar="N")

    # area-stats
    ast = sub.add_parser("area-stats", help="Per-locality price/area summary")
    ast.add_argument(
        "--property-type",
        required=True,
        choices=["flat", "house", "land", "commercial"],
    )
    ast.add_argument(
        "--min-listings",
        type=int,
        default=3,
        metavar="N",
        help="Minimum listings per locality (default: 3)",
    )

    # recent
    rec = sub.add_parser("recent", help="Recently seen listings")
    rec.add_argument("--hours", type=int, default=24, metavar="N")
    rec.add_argument("--listing-type", choices=["sale", "rent"], default=None)
    rec.add_argument(
        "--property-type",
        choices=["flat", "house", "land", "commercial"],
        default=None,
    )

    # alerts
    al = sub.add_parser("alerts", help="New listings and price drops")
    al.add_argument("--hours", type=int, default=24, metavar="N")
    al.add_argument(
        "--min-drop",
        type=float,
        default=5.0,
        metavar="PCT",
        help="Minimum price drop %% to report (default: 5.0)",
    )

    return p


def main() -> None:
    args = _build_parser().parse_args()
    handlers = {
        "price-trend": cmd_price_trend,
        "area-stats": cmd_area_stats,
        "recent": cmd_recent,
        "alerts": cmd_alerts,
    }
    asyncio.run(handlers[args.command](args))


if __name__ == "__main__":
    main()
