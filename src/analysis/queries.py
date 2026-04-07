"""Read-only analytical queries over the listings and price_history tables."""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from src.storage.models import Listing


@dataclass
class PriceTrendPoint:
    """One data point in a monthly price trend series."""

    month: str  # "YYYY-MM"
    avg_price_czk: int
    count: int


@dataclass
class AreaStat:
    """Aggregated price and area statistics for a single locality."""

    locality: str
    avg_price_czk: int
    median_area_m2: float | None
    listing_count: int


async def price_trend(
    session: AsyncSession,
    locality: str,
    property_type: str,
    months: int = 12,
) -> list[PriceTrendPoint]:
    """Monthly average price for a locality + property_type combination.

    Searches locality with a case-insensitive substring match so callers
    can pass "Praha" to match "Praha, Praha 1", "Praha, Praha 5", etc.

    Returns one point per calendar month (oldest → newest) covering the
    last `months` months.  Only price_history rows for active listings with
    a non-null price are included.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=months * 31)
    rows = await session.execute(
        text(
            """
            SELECT
                to_char(ph.recorded_at, 'YYYY-MM') AS month,
                ROUND(AVG(ph.price_czk))::bigint    AS avg_price_czk,
                COUNT(*)::int                        AS cnt
            FROM price_history ph
            JOIN listings l ON l.id = ph.listing_id
            WHERE l.locality ILIKE :locality_pat
              AND l.property_type = :property_type
              AND ph.recorded_at >= :cutoff
            GROUP BY month
            ORDER BY month
            """
        ),
        {
            "locality_pat": f"%{locality}%",
            "property_type": property_type,
            "cutoff": cutoff,
        },
    )
    return [
        PriceTrendPoint(
            month=r.month,
            avg_price_czk=r.avg_price_czk,
            count=r.cnt,
        )
        for r in rows
    ]


async def area_stats(
    session: AsyncSession,
    property_type: str,
    min_listings: int = 3,
) -> list[AreaStat]:
    """Average price and median area per locality for a given property type.

    Only active listings with a non-null price and locality are included.
    Localities with fewer than `min_listings` are excluded.
    Results are sorted by avg_price_czk descending.
    """
    rows = await session.execute(
        text(
            """
            SELECT
                locality,
                ROUND(AVG(price_czk))::bigint                            AS avg_price_czk,
                PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY area_m2)     AS median_area_m2,
                COUNT(*)::int                                             AS listing_count
            FROM listings
            WHERE property_type = :property_type
              AND is_active = TRUE
              AND price_czk IS NOT NULL
              AND locality IS NOT NULL
            GROUP BY locality
            HAVING COUNT(*) >= :min_listings
            ORDER BY avg_price_czk DESC
            """
        ),
        {"property_type": property_type, "min_listings": min_listings},
    )
    return [
        AreaStat(
            locality=r.locality,
            avg_price_czk=r.avg_price_czk,
            median_area_m2=float(r.median_area_m2) if r.median_area_m2 is not None else None,
            listing_count=r.listing_count,
        )
        for r in rows
    ]


async def recent_listings(
    session: AsyncSession,
    since_hours: int = 24,
    listing_type: str | None = None,
    property_type: str | None = None,
) -> list[Listing]:
    """Return active listings first seen within the last `since_hours` hours.

    Optionally filter by listing_type ('sale'/'rent') and/or property_type
    ('flat'/'house'/'land'/'commercial').  Results are ordered newest first.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(hours=since_hours)
    stmt = (
        select(Listing)
        .where(Listing.first_seen_at >= cutoff, Listing.is_active.is_(True))
        .order_by(Listing.first_seen_at.desc())
    )
    if listing_type is not None:
        stmt = stmt.where(Listing.listing_type == listing_type)
    if property_type is not None:
        stmt = stmt.where(Listing.property_type == property_type)

    result = await session.execute(stmt)
    return list(result.scalars().all())
