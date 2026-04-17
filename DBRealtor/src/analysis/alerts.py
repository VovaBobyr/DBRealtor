"""Alert detection: new listings and price drops since a given timestamp."""

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from src.storage.models import Listing


@dataclass
class PriceDrop:
    """A listing whose price fell by at least a given percentage."""

    sreality_id: str
    title: str
    locality: str | None
    url: str
    old_price_czk: int
    new_price_czk: int
    drop_pct: float


async def new_listings_since(
    session: AsyncSession,
    since: datetime,
) -> list[Listing]:
    """Return active listings whose first_seen_at is >= since.

    Ordered by first_seen_at descending (newest first).
    """
    result = await session.execute(
        select(Listing)
        .where(Listing.first_seen_at >= since, Listing.is_active.is_(True))
        .order_by(Listing.first_seen_at.desc())
    )
    return list(result.scalars().all())


async def price_drops_since(
    session: AsyncSession,
    since: datetime,
    min_drop_pct: float = 5.0,
) -> list[PriceDrop]:
    """Return listings where the price dropped by at least min_drop_pct %.

    Considers only price_history entries recorded on or after `since`.
    For each such entry, compares against the immediately preceding price.
    Only active listings are included.

    Results are ordered by drop_pct descending (largest drop first).
    """
    rows = await session.execute(
        text(
            """
            WITH ranked AS (
                SELECT
                    ph.listing_id,
                    ph.price_czk,
                    ph.recorded_at,
                    LAG(ph.price_czk) OVER (
                        PARTITION BY ph.listing_id ORDER BY ph.recorded_at
                    ) AS prev_price_czk
                FROM price_history ph
            )
            SELECT
                l.sreality_id,
                l.title,
                l.locality,
                l.url,
                r.prev_price_czk  AS old_price_czk,
                r.price_czk       AS new_price_czk,
                ROUND(
                    (r.prev_price_czk - r.price_czk)::numeric
                    / r.prev_price_czk * 100,
                    2
                ) AS drop_pct
            FROM ranked r
            JOIN listings l ON l.id = r.listing_id
            WHERE r.recorded_at >= :since
              AND r.prev_price_czk IS NOT NULL
              AND r.price_czk < r.prev_price_czk
              AND (r.prev_price_czk - r.price_czk)::float
                  / r.prev_price_czk * 100 >= :min_drop_pct
              AND l.is_active = TRUE
            ORDER BY drop_pct DESC
            """
        ),
        {"since": since, "min_drop_pct": min_drop_pct},
    )
    return [
        PriceDrop(
            sreality_id=r.sreality_id,
            title=r.title,
            locality=r.locality,
            url=r.url,
            old_price_czk=r.old_price_czk,
            new_price_czk=r.new_price_czk,
            drop_pct=float(r.drop_pct),
        )
        for r in rows
    ]
