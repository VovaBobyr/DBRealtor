"""Initial schema: listings, price_history, scrape_runs.

Revision ID: 0001
Revises:
Create Date: 2026-04-06 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Use raw SQL for the entire migration to avoid SQLAlchemy's automatic
    # CREATE TYPE attempts on each create_table call.
    op.execute("""
        CREATE TYPE listing_type_enum AS ENUM ('sale', 'rent');
        CREATE TYPE property_type_enum AS ENUM ('flat', 'house', 'land', 'commercial');
        CREATE TYPE scrape_run_status_enum AS ENUM ('running', 'success', 'failed');

        CREATE TABLE listings (
            id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            sreality_id TEXT NOT NULL UNIQUE,
            listing_type    listing_type_enum NOT NULL,
            property_type   property_type_enum NOT NULL,
            title           TEXT NOT NULL,
            description     TEXT,
            price_czk       BIGINT,
            area_m2         INTEGER,
            floor           INTEGER,
            locality        TEXT,
            gps_lat         DOUBLE PRECISION,
            gps_lon         DOUBLE PRECISION,
            url             TEXT NOT NULL,
            images          JSONB,
            raw_data        JSONB,
            first_seen_at   TIMESTAMPTZ NOT NULL,
            last_seen_at    TIMESTAMPTZ NOT NULL,
            is_active       BOOLEAN NOT NULL DEFAULT TRUE
        );

        CREATE TABLE price_history (
            id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            listing_id  UUID NOT NULL REFERENCES listings(id) ON DELETE CASCADE,
            price_czk   BIGINT NOT NULL,
            recorded_at TIMESTAMPTZ NOT NULL
        );
        CREATE INDEX ix_price_history_listing_id ON price_history (listing_id);

        CREATE TABLE scrape_runs (
            id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            started_at      TIMESTAMPTZ NOT NULL,
            finished_at     TIMESTAMPTZ,
            listings_found  INTEGER NOT NULL DEFAULT 0,
            listings_new    INTEGER NOT NULL DEFAULT 0,
            listings_updated INTEGER NOT NULL DEFAULT 0,
            errors          JSONB,
            status          scrape_run_status_enum NOT NULL DEFAULT 'running'
        );
    """)


def downgrade() -> None:
    op.drop_table("scrape_runs")
    op.drop_index("ix_price_history_listing_id", table_name="price_history")
    op.drop_table("price_history")
    op.drop_table("listings")

    op.execute("DROP TYPE IF EXISTS scrape_run_status_enum")
    op.execute("DROP TYPE IF EXISTS property_type_enum")
    op.execute("DROP TYPE IF EXISTS listing_type_enum")
