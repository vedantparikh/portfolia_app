from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
from typing import Generator
import redis
from .config import db_settings

# Create SQLAlchemy engine with connection pooling
engine = create_engine(
    db_settings.postgres_url,
    poolclass=QueuePool,
    pool_size=db_settings.POOL_SIZE,
    max_overflow=db_settings.MAX_OVERFLOW,
    pool_timeout=db_settings.POOL_TIMEOUT,
    pool_recycle=db_settings.POOL_RECYCLE,
    echo=False,  # Set to False for production, True for debugging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Redis connection
redis_client = redis.Redis.from_url(
    db_settings.redis_url,
    decode_responses=True,
    socket_connect_timeout=5,
    socket_timeout=5,
    retry_on_timeout=True,
)


def get_db() -> Generator[Session, None, None]:
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """Get database session as context manager."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)


def close_db():
    """Close database connections."""
    engine.dispose()


def health_check() -> bool:
    """Check database health."""
    try:
        print(f"Attempting to connect to: {db_settings.postgres_url}")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print(f"Connection successful: {result.fetchone()}")
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False


def redis_health_check() -> bool:
    """Check Redis health."""
    try:
        redis_client.ping()
        return True
    except Exception:
        return False
