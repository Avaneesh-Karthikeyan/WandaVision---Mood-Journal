import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import AsyncMock, patch

from app.main import app, get_db
from app.database import Base

# Use an in-memory SQLite database for tests
TEST_DATABASE_URL = "sqlite:///./test_journal.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """Create tables before each test, drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client():
    """Test client with overridden DB dependency."""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def mock_sentiment():
    """Mock the OpenAI sentiment analysis to avoid real API calls in tests."""
    mock_result = {"mood": "happy", "reflection": "It sounds like you had a wonderful day!"}
    with patch("app.main.sentiment.analyze_sentiment", new_callable=AsyncMock) as mock:
        mock.return_value = mock_result
        yield mock


@pytest.fixture
def mock_sentiment_sad():
    """Mock sentiment for a sad entry."""
    mock_result = {"mood": "sad", "reflection": "It seems like today was tough — be kind to yourself."}
    with patch("app.main.sentiment.analyze_sentiment", new_callable=AsyncMock) as mock:
        mock.return_value = mock_result
        yield mock
