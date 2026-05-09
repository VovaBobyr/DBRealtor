"""GET /api/trends/price       — monthly avg price trend.
GET /api/trends/new-per-day  — daily new-listing count (same locality/type/months filters).
GET /api/trends/new-listings — daily count, days-window filter (legacy).
"""

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session

router = APIRouter(prefix="/api/trends", tags=["trends"])


class PriceTrendPoint(BaseModel):
    period: str
    avg_price_czk: int
    avg_price_per_m2: int | None
    count: int


class NewListingsDayPoint(BaseModel):
    day: str
    count: int


class NewPerDayPoint(BaseModel):
    date: str
    count: int


@router.get("/price", response_model=list[PriceTrendPoint])
async def get_price_trend(
    locality: str = Query(default="Praha", description="Locality substring filter"),
    property_type: str = Query(default="flat", description="flat|house|land|commercial"),
    days: int = Query(default=365, ge=7, le=730, description="Number of days to look back"),
    flat_type: str | None = Query(default=None, description="Flat subtype filter (e.g. 2+kk), only applies when property_type=flat"),
    session: AsyncSession = Depends(get_session),
) -> list[PriceTrendPoint]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    if days <= 30:
        period_expr = "DATE(ph.recorded_at AT TIME ZONE 'Europe/Prague')::text"
    elif days <= 180:
        period_expr = "to_char(DATE_TRUNC('week', ph.recorded_at AT TIME ZONE 'Europe/Prague'), 'YYYY-MM-DD')"
    else:
        period_expr = "to_char(ph.recorded_at AT TIME ZONE 'Europe/Prague', 'YYYY-MM')"
    flat_type_clause = (
        "AND l.raw_data->'categorySubCb'->>'name' = :flat_type"
        if flat_type and property_type == "flat"
        else ""
    )
    params: dict = {
        "locality_pat": f"%{locality}%",
        "property_type": property_type,
        "cutoff": cutoff,
    }
    if flat_type and property_type == "flat":
        params["flat_type"] = flat_type

    rows = await session.execute(
        text(
            f"""
            SELECT
                {period_expr}                                AS period,
                ROUND(AVG(ph.price_czk))::bigint             AS avg_price_czk,
                CASE
                    WHEN AVG(l.area_m2) > 0
                    THEN ROUND(AVG(ph.price_czk) / NULLIF(AVG(l.area_m2), 0))::bigint
                    ELSE NULL
                END                                          AS avg_price_per_m2,
                COUNT(*)::int                                AS cnt
            FROM price_history ph
            JOIN listings l ON l.id = ph.listing_id
            WHERE l.locality ILIKE :locality_pat
              AND l.property_type = :property_type
              AND ph.recorded_at >= :cutoff
              AND ph.price_czk IS NOT NULL
              {flat_type_clause}
            GROUP BY period
            ORDER BY period
            """
        ),
        params,
    )

    return [
        PriceTrendPoint(
            period=r.period,
            avg_price_czk=r.avg_price_czk,
            avg_price_per_m2=r.avg_price_per_m2,
            count=r.cnt,
        )
        for r in rows
    ]


def _drop_initial_load_spike(points: list[NewPerDayPoint]) -> list[NewPerDayPoint]:
    # The first scraper run backfills every currently-active listing on the
    # same calendar day, producing a one-off spike that dwarfs real daily
    # counts and distorts the chart's Y-axis. If the earliest date's count is
    # more than 3x the median of the remaining days, treat it as a seed
    # artifact and drop it. Dynamic so it self-corrects after re-seeds.
    if len(points) < 3:
        return points
    rest = points[1:]
    rest_sorted = sorted(p.count for p in rest)
    n = len(rest_sorted)
    median = (
        rest_sorted[n // 2]
        if n % 2
        else (rest_sorted[n // 2 - 1] + rest_sorted[n // 2]) / 2
    )
    if median > 0 and points[0].count > 3 * median:
        return rest
    return points


@router.get("/new-per-day", response_model=list[NewPerDayPoint])
async def get_new_per_day(
    locality: str = Query(default="Praha", description="Locality substring filter"),
    property_type: str = Query(default="flat", description="flat|house|land|commercial"),
    days: int = Query(default=365, ge=7, le=730, description="Number of days to look back"),
    flat_type: str | None = Query(default=None, description="Flat subtype filter (e.g. 2+kk), only applies when property_type=flat"),
    session: AsyncSession = Depends(get_session),
) -> list[NewPerDayPoint]:
    """Count of new listings per calendar day, filtered by locality and property type.

    Uses the same locality/property_type/days parameters as /price so both
    charts on the Trends page share a single set of controls.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    if days <= 30:
        date_expr = "DATE(first_seen_at AT TIME ZONE 'Europe/Prague')::text"
    elif days <= 180:
        date_expr = "to_char(DATE_TRUNC('week', first_seen_at AT TIME ZONE 'Europe/Prague'), 'YYYY-MM-DD')"
    else:
        date_expr = "to_char(first_seen_at AT TIME ZONE 'Europe/Prague', 'YYYY-MM')"
    flat_type_clause = (
        "AND raw_data->'categorySubCb'->>'name' = :flat_type"
        if flat_type and property_type == "flat"
        else ""
    )
    params: dict = {
        "locality_pat": f"%{locality}%",
        "property_type": property_type,
        "cutoff": cutoff,
    }
    if flat_type and property_type == "flat":
        params["flat_type"] = flat_type

    rows = await session.execute(
        text(
            f"""
            SELECT
                {date_expr}      AS date,
                COUNT(*)::int    AS count
            FROM listings
            WHERE locality      ILIKE :locality_pat
              AND property_type = :property_type
              AND first_seen_at >= :cutoff
              {flat_type_clause}
            GROUP BY date
            ORDER BY date
            """
        ),
        params,
    )
    points = [NewPerDayPoint(date=str(r.date), count=r.count) for r in rows]
    return _drop_initial_load_spike(points)


@router.get("/new-listings", response_model=list[NewListingsDayPoint])
async def get_new_listings_trend(
    days: int = Query(default=30, ge=7, le=365, description="Number of days to look back"),
    session: AsyncSession = Depends(get_session),
) -> list[NewListingsDayPoint]:
    """Daily count of listings first seen within the given window.

    Counts all listings regardless of current active status — a listing that
    appeared on day X and was later delisted still counts for that day.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    rows = await session.execute(
        text(
            """
            SELECT
                DATE(first_seen_at AT TIME ZONE 'Europe/Prague') AS day,
                COUNT(*)::int                                     AS count
            FROM listings
            WHERE first_seen_at >= :cutoff
            GROUP BY day
            ORDER BY day
            """
        ),
        {"cutoff": cutoff},
    )
    return [NewListingsDayPoint(day=str(r.day), count=r.count) for r in rows]
