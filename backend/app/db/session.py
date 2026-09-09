import os
import re
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.core.config import settings
from backend.app.db.base import Base
import backend.app.db.models  # Ensure models are loaded

def get_async_database_url(url: str) -> str:
    """Converts a standard database URL to its async driver equivalent."""
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://") and not url.startswith("postgresql+asyncpg://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif url.startswith("sqlite://") and not url.startswith("sqlite+aiosqlite://"):
        url = url.replace("sqlite://", "sqlite+aiosqlite://", 1)
    return url

def get_sync_database_url(url: str) -> str:
    """Converts an async database URL to a sync driver equivalent for migrations."""
    if url.startswith("postgresql+asyncpg://"):
        url = url.replace("postgresql+asyncpg://", "postgresql://", 1)
    elif url.startswith("sqlite+aiosqlite://"):
        url = url.replace("sqlite+aiosqlite://", "sqlite://", 1)
    return url

ASYNC_DATABASE_URL = get_async_database_url(settings.DATABASE_URL)
SYNC_DATABASE_URL = get_sync_database_url(settings.DATABASE_URL)

# Async engine & session
connect_args = {}
if ASYNC_DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=False,
    future=True,
    connect_args=connect_args
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Sync engine & session for migrations/tests
sync_connect_args = {}
if SYNC_DATABASE_URL.startswith("sqlite"):
    sync_connect_args["check_same_thread"] = False

sync_engine = create_engine(
    SYNC_DATABASE_URL,
    echo=False,
    connect_args=sync_connect_args
)

SyncSessionLocal = sessionmaker(
    bind=sync_engine,
    autocommit=False,
    autoflush=False
)

async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    """Initializes all database tables asynchronously on application startup."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

def init_sync_db():
    """Initializes all database tables synchronously."""
    Base.metadata.create_all(bind=sync_engine)

try:
    init_sync_db()
except Exception:
    pass

