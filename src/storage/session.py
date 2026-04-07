"""Async SQLAlchemy engine and session factory.

Reads DATABASE_URL from the environment (via .env).
Call get_session() to obtain an AsyncSession; it commits on clean exit
and rolls back on exception.
"""

import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

load_dotenv()

_DATABASE_URL: str = os.environ["DATABASE_URL"]

engine: AsyncEngine = create_async_engine(
    _DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    echo=False,
)

_session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Async context manager that yields a committed AsyncSession.

    Commits on clean exit; rolls back and re-raises on any exception.
    """
    async with _session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
