"""Database configuration and session management."""

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

# Check if using SQLite
is_sqlite = settings.USE_SQLITE or "sqlite" in settings.DATABASE_URL.lower()

if is_sqlite:
    # SQLite configuration
    engine = create_engine(
        settings.SQLITE_URL.replace("sqlite+aiosqlite://", "sqlite://"),
        connect_args={"check_same_thread": False}
    )
    
    async_engine = create_async_engine(
        "sqlite+aiosqlite:///./forex_ai_signals.db",
        connect_args={"check_same_thread": False}
    )
else:
    # PostgreSQL configuration
    engine = create_engine(
        settings.DATABASE_URL.replace("+asyncpg", ""),
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20
    )
    
    async_engine = create_async_engine(
        settings.DATABASE_URL_ASYNC,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20
    )

# Session factories
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
AsyncSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=async_engine, class_=AsyncSession)

# Base class for models
Base = declarative_base()


async def get_db():
    """Dependency to get database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
