"""Integration tests for analysis/queries.py and analysis/alerts.py.

Requires a live PostgreSQL instance (DATABASE_URL in .env).
Uses the same db fixture pattern as tests/storage/test_repository.py —
each test gets a clean slate via TRUNCATE.
"""

import os
from datetime import datetime, timedelta, timezone

import pytest
import pytest_asyncio
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.analysis.alerts import new_listings_since, price_drops_since
from src.analysis.queries import area_stats, price_trend, recent_listings
from src.scraper.parser import ListingData
from src.storage.repository import upsert_listing

load_dotenv()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def db():
    """Fresh async engine + truncated tables for each test."""
    engine = create_async_engine(os.environ["DATABASE_URL"], echo=False)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with factory() as s:
        await s.execute(
            text("TRUNCATE listings, price_history, scrape_runs CASCADE")
        )
        await s.commit()

    yield factory

    await engine.dispose()


def _listing(**kwargs) -> ListingData:
    """Minimal valid ListingData; override via kwargs."""
    defaults: dict = {
        "sreality_id": "1",
        "listing_type": "sale",
        "property_type": "flat",
        "title": "Test Flat",
        "url": "https://www.sreality.cz/detail/prodej/byt/1+kk/x/1",
        "price_czk": 5_000_000,
        "locality": "Praha, Praha 1",
        "area_m2": 50,
    }
    defaults.update(kwargs)
    return ListingData(**defaults)


async def _insert(factory, listing: ListingData) -> None:
    async with factory() as session:
        await upsert_listing(session, listing)
        await session.commit()


# ---------------------------------------------------------------------------
# recent_listings
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_recent_listings_returns_listings_within_window(db):
    await _insert(db, _listing(sreality_id="10"))

    async with db() as session:
        results = await recent_listings(session, since_hours=1)

    assert len(results) == 1
    assert results[0].sreality_id == "10"


@pytest.mark.asyncio
async def test_recent_listings_excludes_old_listings(db):
    """A listing with first_seen_at before the cutoff should not appear."""
    await _insert(db, _listing(sreality_id="10"))

    # Manually backdate first_seen_at to 2 hours ago.
    async with db() as session:
        await session.execute(
            text(
                "UPDATE listings SET first_seen_at = NOW() - INTERVAL '2 hours' "
                "WHERE sreality_id = '10'"
            )
        )
        await session.commit()

    async with db() as session:
        results = await recent_listings(session, since_hours=1)

    assert results == []


@pytest.mark.asyncio
async def test_recent_listings_filters_by_listing_type(db):
    await _insert(db, _listing(sreality_id="11", listing_type="sale"))
    await _insert(db, _listing(sreality_id="12", listing_type="rent"))

    async with db() as session:
        results = await recent_listings(session, since_hours=1, listing_type="rent")

    assert len(results) == 1
    assert results[0].sreality_id == "12"


@pytest.mark.asyncio
async def test_recent_listings_filters_by_property_type(db):
    await _insert(db, _listing(sreality_id="21", property_type="flat"))
    await _insert(db, _listing(sreality_id="22", property_type="house"))

    async with db() as session:
        results = await recent_listings(session, since_hours=1, property_type="house")

    assert len(results) == 1
    assert results[0].sreality_id == "22"


# ---------------------------------------------------------------------------
# area_stats
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_area_stats_groups_by_locality(db):
    for i, (price, area) in enumerate([(5_000_000, 50), (6_000_000, 60), (7_000_000, 70)]):
        await _insert(
            db,
            _listing(
                sreality_id=str(100 + i),
                locality="Praha, Praha 2",
                price_czk=price,
                area_m2=area,
            ),
        )

    async with db() as session:
        stats = await area_stats(session, property_type="flat", min_listings=1)

    assert len(stats) == 1
    assert stats[0].locality == "Praha, Praha 2"
    assert stats[0].listing_count == 3
    assert stats[0].avg_price_czk == 6_000_000
    assert stats[0].median_area_m2 == 60.0


@pytest.mark.asyncio
async def test_area_stats_respects_min_listings(db):
    await _insert(db, _listing(sreality_id="201", locality="Brno, Brno-střed"))
    await _insert(db, _listing(sreality_id="202", locality="Brno, Brno-střed"))
    await _insert(db, _listing(sreality_id="203", locality="Ostrava, Ostrava 1"))

    async with db() as session:
        stats = await area_stats(session, property_type="flat", min_listings=2)

    localities = [s.locality for s in stats]
    assert "Brno, Brno-střed" in localities
    assert "Ostrava, Ostrava 1" not in localities


# ---------------------------------------------------------------------------
# price_trend
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_price_trend_returns_monthly_buckets(db):
    # Insert a listing then manually add a second price_history row
    # so we have two entries that fall in different months.
    await _insert(db, _listing(sreality_id="301", price_czk=5_000_000, locality="Praha, Praha 3"))

    async with db() as session:
        # Backdate the first price_history row to last month.
        await session.execute(
            text(
                "UPDATE price_history ph "
                "SET recorded_at = date_trunc('month', NOW()) - INTERVAL '1 month' "
                "FROM listings l "
                "WHERE ph.listing_id = l.id AND l.sreality_id = '301'"
            )
        )
        # Insert a new price_history row for this month.
        await session.execute(
            text(
                "INSERT INTO price_history (id, listing_id, price_czk, recorded_at) "
                "SELECT gen_random_uuid(), l.id, 4800000, NOW() "
                "FROM listings l WHERE l.sreality_id = '301'"
            )
        )
        await session.commit()

    async with db() as session:
        points = await price_trend(
            session, locality="Praha 3", property_type="flat", months=3
        )

    assert len(points) == 2
    # Oldest first.
    assert points[0].avg_price_czk == 5_000_000
    assert points[1].avg_price_czk == 4_800_000


@pytest.mark.asyncio
async def test_price_trend_empty_for_unknown_locality(db):
    await _insert(db, _listing(sreality_id="401", locality="Praha, Praha 4"))

    async with db() as session:
        points = await price_trend(session, locality="Brno", property_type="flat")

    assert points == []


# ---------------------------------------------------------------------------
# new_listings_since (alerts)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_new_listings_since_returns_recent(db):
    await _insert(db, _listing(sreality_id="501"))
    since = datetime.now(timezone.utc) - timedelta(hours=1)

    async with db() as session:
        results = await new_listings_since(session, since)

    assert len(results) == 1
    assert results[0].sreality_id == "501"


@pytest.mark.asyncio
async def test_new_listings_since_excludes_old(db):
    await _insert(db, _listing(sreality_id="502"))
    async with db() as session:
        await session.execute(
            text(
                "UPDATE listings SET first_seen_at = NOW() - INTERVAL '2 hours' "
                "WHERE sreality_id = '502'"
            )
        )
        await session.commit()

    since = datetime.now(timezone.utc) - timedelta(hours=1)
    async with db() as session:
        results = await new_listings_since(session, since)

    assert results == []


# ---------------------------------------------------------------------------
# price_drops_since (alerts)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_price_drops_since_detects_drop(db):
    await _insert(db, _listing(sreality_id="601", price_czk=5_000_000))
    # Second upsert with lower price records another price_history row.
    await _insert(db, _listing(sreality_id="601", price_czk=4_000_000))

    since = datetime.now(timezone.utc) - timedelta(hours=1)
    async with db() as session:
        drops = await price_drops_since(session, since, min_drop_pct=5.0)

    assert len(drops) == 1
    assert drops[0].sreality_id == "601"
    assert drops[0].old_price_czk == 5_000_000
    assert drops[0].new_price_czk == 4_000_000
    assert drops[0].drop_pct == pytest.approx(20.0, abs=0.1)


@pytest.mark.asyncio
async def test_price_drops_since_ignores_small_drops(db):
    await _insert(db, _listing(sreality_id="602", price_czk=5_000_000))
    await _insert(db, _listing(sreality_id="602", price_czk=4_950_000))  # 1% drop

    since = datetime.now(timezone.utc) - timedelta(hours=1)
    async with db() as session:
        drops = await price_drops_since(session, since, min_drop_pct=5.0)

    assert drops == []


@pytest.mark.asyncio
async def test_price_drops_since_ignores_price_increases(db):
    await _insert(db, _listing(sreality_id="603", price_czk=4_000_000))
    await _insert(db, _listing(sreality_id="603", price_czk=5_000_000))  # increase

    since = datetime.now(timezone.utc) - timedelta(hours=1)
    async with db() as session:
        drops = await price_drops_since(session, since, min_drop_pct=5.0)

    assert drops == []
