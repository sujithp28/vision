"""Database session management"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@localhost:5432/visionforge"
)

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verify connections before using
)

# Create session factory
SessionLocal = sessionmaker(bind=engine, class_=Session, expire_on_commit=False)


def get_session() -> Generator[Session, None, None]:
    """Get database session for dependency injection
    
    Usage in FastAPI:
        @router.get("/")
        async def my_route(db: Session = Depends(get_session)):
            pass
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
