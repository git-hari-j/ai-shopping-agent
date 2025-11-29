from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from config import settings
import os
import logging

logger = logging.getLogger(__name__)

# Logic to handle different database drivers
database_url = settings.DATABASE_URL
connect_args = {}

if database_url.startswith("postgresql"):
    # Ensure usage of asyncpg driver
    if not "+asyncpg" in database_url:
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
    logger.info("Using PostgreSQL database")

elif database_url.startswith("sqlite"):
    # Ensure usage of aiosqlite driver
    if not "+aiosqlite" in database_url:
        database_url = database_url.replace("sqlite://", "sqlite+aiosqlite://")
    # SQLite specific args for concurrency
    connect_args = {"check_same_thread": False}
    logger.info("Using SQLite database")

# Create async engine
engine = create_async_engine(
    database_url,
    echo=False,
    future=True,
    connect_args=connect_args
)

# Create session factory
async_session_factory = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession
)

# Base class for models
class Base(DeclarativeBase):
    pass

# Dependency for FastAPI
async def get_db():
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()
