"""Repository layer: upsert listings, track price history, manage scrape runs.

All functions accept an AsyncSession and flush (not commit) changes — the
caller is responsible for committing the session.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.scraper.parser import ListingData
from src.storage.models import Listing, PriceHistory, ScrapeRun


@dataclass
class ScrapeRunData:
    """Mutable accumulator for a scrape run's statistics."""

    id: uuid.UUID = field(default_factory=uuid.uuid4)
    started_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    finished_at: datetime | None = None
    listings_found: int = 0
    listings_new: int = 0
    listings_updated: int = 0
    errors: list[str] = field(default_factory=list)
    status: str = "running"


async def upsert_listing(
    session: AsyncSession,
    listing: ListingData,
) -> tuple[str, uuid.UUID]:
    """Insert a new listing or update an existing one atomically.

    Uses PostgreSQL INSERT ... ON CONFLICT (sreality_id) DO UPDATE to avoid
    any race condition between concurrent scrape processes.

    Price change detection works by reading the existing price_czk *before*
    the upsert (a simple SELECT).  The subsequent upsert is atomic — even if
    two processes race, only one row per sreality_id can ever exist.

    Returns:
        ("new",       listing_id) — newly inserted.
        ("updated",   listing_id) — price or field change detected.
        ("unchanged", listing_id) — row already matched current data.
    """
    now = datetime.now(timezone.utc)

    # Read existing row so we can detect price changes and return the right status.
    result = await session.execute(
        select(Listing.id, Listing.price_czk).where(
            Listing.sreality_id == listing.sreality_id
        )
    )
    existing = result.one_or_none()
    is_new = existing is None
    price_changed = (
        not is_new and existing.price_czk != listing.price_czk
    )

    new_id = existing.id if existing is not None else uuid.uuid4()

    stmt = pg_insert(Listing).values(
        id=new_id,
        sreality_id=listing.sreality_id,
        listing_type=listing.listing_type,
        property_type=listing.property_type,
        title=listing.title,
        description=listing.description,
        price_czk=listing.price_czk,
        area_m2=listing.area_m2,
        floor=listing.floor,
        locality=listing.locality,
        gps_lat=listing.gps_lat,
        gps_lon=listing.gps_lon,
        url=listing.url,
        images=listing.images,
        raw_data=listing.raw_data,
        first_seen_at=now,
        last_seen_at=now,
        is_active=True,
    )
    stmt = stmt.on_conflict_do_update(
        index_elements=["sreality_id"],
        set_=dict(
            listing_type=stmt.excluded.listing_type,
            property_type=stmt.excluded.property_type,
            title=stmt.excluded.title,
            description=stmt.excluded.description,
            price_czk=stmt.excluded.price_czk,
            area_m2=stmt.excluded.area_m2,
            floor=stmt.excluded.floor,
            locality=stmt.excluded.locality,
            gps_lat=stmt.excluded.gps_lat,
            gps_lon=stmt.excluded.gps_lon,
            url=stmt.excluded.url,
            images=stmt.excluded.images,
            raw_data=stmt.excluded.raw_data,
            last_seen_at=stmt.excluded.last_seen_at,
            is_active=True,
            # first_seen_at is intentionally excluded — never overwrite it
        ),
    ).returning(Listing.id)

    result = await session.execute(stmt)
    listing_id: uuid.UUID = result.scalar_one()

    if is_new and listing.price_czk is not None:
        session.add(
            PriceHistory(
                listing_id=listing_id,
                price_czk=listing.price_czk,
                recorded_at=now,
            )
        )
        return ("new", listing_id)

    if price_changed and listing.price_czk is not None:
        session.add(
            PriceHistory(
                listing_id=listing_id,
                price_czk=listing.price_czk,
                recorded_at=now,
            )
        )
        return ("updated", listing_id)

    return ("unchanged", listing_id)


async def mark_inactive(
    session: AsyncSession,
    active_sreality_ids: list[str],
) -> int:
    """Set is_active=False for every active listing NOT in active_sreality_ids.

    Returns the count of rows marked inactive.
    """
    if not active_sreality_ids:
        return 0

    result = await session.execute(
        update(Listing)
        .where(
            Listing.is_active.is_(True),
            Listing.sreality_id.not_in(active_sreality_ids),
        )
        .values(is_active=False)
        .returning(Listing.id)
    )
    return len(result.fetchall())


async def open_scrape_run(session: AsyncSession) -> ScrapeRunData:
    """Insert a new scrape_run row in 'running' state and return its data."""
    run = ScrapeRunData()
    session.add(
        ScrapeRun(
            id=run.id,
            started_at=run.started_at,
            status="running",
        )
    )
    await session.flush()
    return run


async def close_scrape_run(
    session: AsyncSession,
    run: ScrapeRunData,
    status: str = "success",
) -> None:
    """Update the scrape_run row with final counts and status."""
    now = datetime.now(timezone.utc)
    run.finished_at = now
    run.status = status

    await session.execute(
        update(ScrapeRun)
        .where(ScrapeRun.id == run.id)
        .values(
            finished_at=now,
            listings_found=run.listings_found,
            listings_new=run.listings_new,
            listings_updated=run.listings_updated,
            errors=run.errors if run.errors else None,
            status=status,
        )
    )
