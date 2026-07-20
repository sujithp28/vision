"""Pytest configuration and fixtures"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from packages.database.models import Base


@pytest.fixture
def test_db_session():
    """Create in-memory test database session"""
    # Use SQLite in-memory for fast tests
    engine = create_engine("sqlite:///:memory:")
    
    # Create all tables
    Base.metadata.create_all(engine)
    
    # Create session
    TestSessionLocal = sessionmaker(bind=engine)
    session = TestSessionLocal()
    
    yield session
    
    # Cleanup
    session.close()
    Base.metadata.drop_all(engine)


@pytest.fixture
def mock_settings(monkeypatch):
    """Mock settings for tests"""
    monkeypatch.setenv("SECRET_KEY", "test-secret-key-12345678901234567890")
    monkeypatch.setenv("DEBUG", "True")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    monkeypatch.setenv("ENVIRONMENT", "test")
