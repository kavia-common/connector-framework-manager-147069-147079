"""Database connection and session management."""
from __future__ import annotations

from contextlib import contextmanager
from typing import Generator, Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.pool import NullPool

from src.config.settings import settings

# Get database URL from settings (env-driven through pydantic-settings)
DATABASE_URL = settings.database_url

# Engine configuration:
# - Use NullPool for serverless/dev environments to avoid lingering connections
# - For SQLite, set check_same_thread=False
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool if DATABASE_URL.startswith("postgresql") else None,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    future=True,
)

# Session factory with typing
SessionLocal: sessionmaker[Session] = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)

# Declarative Base
Base = declarative_base()


# PUBLIC_INTERFACE
def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get a SQLAlchemy session for FastAPI routes.

    Yields:
        Session: Database session which is closed after the request finishes.
    """
    db: Session = SessionLocal()
    try:
        yield db
        # Do not commit implicitly; route handlers should explicitly commit when needed
    finally:
        db.close()


@contextmanager
def db_session() -> Iterator[Session]:
    """
    Context manager for service-layer usage outside FastAPI dependency system.

    Example:
        with db_session() as db:
            ...
    """
    session: Session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
