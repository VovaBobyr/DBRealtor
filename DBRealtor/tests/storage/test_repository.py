"""Integration tests for repository.py.

Requires a live PostgreSQL instance (DATABASE_URL in .env).
Each test creates a fresh engine (function scope) to avoid asyncpg
event-loop binding issues. The truncate_tables fixture clears all
test tables before each test.
"""

import os

import pytest
import pytest_asyncio
from dotenv import load_dotenv
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.scraper.parser import ListingData
from src.storage.models import Listing, PriceHistory, ScrapeRun
from src.storage.repository import (
    close_scrape_run,
    mark_inactive,
    open_scrape_run,
    upsert_listing,
)

load_dotenv()


@pytest_asyncio.fixture
async def db(tmp_path):
    """Create a fresh async engine + session factory per test, then dispose."""
    engine = create_async_engine(os.environ["DATABASE_URL"], echo=False)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with factory() as s:
        await s.execute(
            text("TRUNCATE listings, price_history, scrape_runs CASCADE")
        )
        await s.commit()

    yield factory

    await engine.dispose()


def _make_listing(**kwargs) -> ListingData:
    """Create a minimal valid ListingData; override fields via kwargs."""
    defaults: dict = {
        "sreality_id": "99999",
        "listing_type": "sale",
        "property_type": "flat",
        "title": "Test Listing",
        "url": "https://www.sreality.cz/detail/prodej/byt/1+kk/x/99999",
        "price_czk": 5_000_000,
        "locality": "Praha, Praha 1",
    }
    defaults.update(kwargs)
    return ListingData(**defaults)


# ---------------------------------------------------------------------------
# upsert_listing tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_upsert_new_listing_returns_new_and_inserts_row(db):
    """Upserting a listing that doesn't exist should return 'new'."""
    async with db() as session:
        status, listing_id = await upsert_listing(session, _make_listing())
        await session.commit()

    assert status == "new"

    async with db() as session:
        row = (
            await session.execute(
                select(Listing).where(Listing.sreality_id == "99999")
            )
        ).scalar_one()
        assert row.title == "Test Listing"
        assert row.price_czk == 5_000_000
        assert row.is_active is True
        assert row.id == listing_id

        ph_rows = (
            await session.execute(
                select(PriceHistory).where(PriceHistory.listing_id == listing_id)
            )
        ).scalars().all()
        assert len(ph_rows) == 1
        assert ph_rows[0].price_czk == 5_000_000


@pytest.mark.asyncio
async def test_upsert_price_change_records_history(db):
    """A second upsert with a different price should add a price_history row."""
    async with db() as session:
        _, listing_id = await upsert_listing(session, _make_listing(price_czk=5_000_000))
        await session.commit()

    async with db() as session:
        status, _ = await upsert_listing(session, _make_listing(price_czk=4_500_000))
        await session.commit()

    assert status == "updated"

    async with db() as session:
        ph_rows = (
            await session.execute(
                select(PriceHistory)
                .where(PriceHistory.listing_id == listing_id)
                .order_by(PriceHistory.recorded_at)
            )
        ).scalars().all()
        assert len(ph_rows) == 2
        assert ph_rows[0].price_czk == 5_000_000
        assert ph_rows[1].price_czk == 4_500_000


@pytest.mark.asyncio
async def test_upsert_no_price_change_returns_unchanged(db):
    """Re-upserting with identical price should return 'unchanged'."""
    async with db() as session:
        await upsert_listing(session, _make_listing())
        await session.commit()

    async with db() as session:
        status, _ = await upsert_listing(session, _make_listing())
        await session.commit()

    assert status == "unchanged"


# ---------------------------------------------------------------------------
# mark_inactive tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_mark_inactive_deactivates_unseen_listings(db):
    """Listings not in the active ID list should be marked inactive."""
    async with db() as session:
        for sid in ["100", "200", "300"]:
            await upsert_listing(session, _make_listing(sreality_id=sid))
        await session.commit()

    async with db() as session:
        count = await mark_inactive(session, active_sreality_ids=["100"])
        await session.commit()

    assert count == 2

    async with db() as session:
        rows = (await session.execute(select(Listing))).scalars().all()
        activity = {r.sreality_id: r.is_active for r in rows}

    assert activity["100"] is True
    assert activity["200"] is False
    assert activity["300"] is False


# ---------------------------------------------------------------------------
# concurrent upsert — race condition regression test
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_concurrent_upserts_produce_one_row(db):
    """Two concurrent upserts for the same sreality_id must not raise and
    must leave exactly one row in listings."""
    import asyncio

    async def do_upsert(price: int) -> str:
        async with db() as session:
            status, _ = await upsert_listing(session, _make_listing(price_czk=price))
            await session.commit()
        return status

    results = await asyncio.gather(
        do_upsert(5_000_000),
        do_upsert(5_000_000),
    )

    # Both must succeed (no exception).
    assert set(results) <= {"new", "unchanged", "updated"}

    # Exactly one row in the DB.
    async with db() as session:
        rows = (
            await session.execute(
                select(Listing).where(Listing.sreality_id == "99999")
            )
        ).scalars().all()
    assert len(rows) == 1


# ---------------------------------------------------------------------------
# scrape_run tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_open_and_close_scrape_run(db):
    """open_scrape_run inserts a 'running' row; close_scrape_run finalises it."""
    async with db() as session:
        run = await open_scrape_run(session)
        await session.commit()

    async with db() as session:
        db_run = (
            await session.execute(
                select(ScrapeRun).where(ScrapeRun.id == run.id)
            )
        ).scalar_one()
        assert db_run.status == "running"
        assert db_run.finished_at is None

    run.listings_found = 10
    run.listings_new = 8
    run.listings_updated = 2

    async with db() as session:
        await close_scrape_run(session, run, status="success")
        await session.commit()

    async with db() as session:
        db_run = (
            await session.execute(
                select(ScrapeRun).where(ScrapeRun.id == run.id)
            )
        ).scalar_one()
        assert db_run.status == "success"
        assert db_run.finished_at is not None
        assert db_run.listings_found == 10
        assert db_run.listings_new == 8
        assert db_run.listings_updated == 2
