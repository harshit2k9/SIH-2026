"""
Test configuration and fixtures for SIH-2026 testing suite.
"""
import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator
import uuid
from datetime import datetime, timedelta
import jwt

# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://admin:secretpassword@localhost:5432/sih26_test"


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    yield engine
    await engine.dispose()


@pytest.fixture
async def test_db(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session with automatic rollback."""
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client(test_db) -> AsyncGenerator[AsyncClient, None]:
    """Create test HTTP client with database override."""
    from main import app
    from database import get_pool

    # Override database dependency
    async def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    """Sample test user data."""
    return {
        "id": str(uuid.uuid4()),
        "email": "test@example.com",
        "full_name": "Test User",
        "roles": ["investigator"],
        "department_id": str(uuid.uuid4()),
    }


@pytest.fixture
def valid_jwt_token(test_user_data):
    """Generate a valid JWT token for testing."""
    payload = {
        "sub": test_user_data["id"],
        "email": test_user_data["email"],
        "roles": test_user_data["roles"],
        "department_id": test_user_data["department_id"],
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(minutes=30),
        "jti": str(uuid.uuid4()),
        "aud": "sddms-api",
        "iss": "sddms-auth-service"
    }

    # Note: In real tests, use actual test keys
    # For now, return payload for mocking
    return payload


@pytest.fixture
def sample_pdf_content():
    """Sample PDF content for testing."""
    return b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\ntrailer\n<<\n/Size 1\n/Root 1 0 R\n>>\n"


@pytest.fixture
def sample_image_content():
    """Sample image content for testing."""
    # Minimal JPEG header
    return b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xd9"


# Test markers
def pytest_configure(config):
    """Configure custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests (fast, isolated)")
    config.addinivalue_line("markers", "integration: Integration tests (medium speed)")
    config.addinivalue_line("markers", "e2e: End-to-end tests (slow, complete workflows)")
    config.addinivalue_line("markers", "security: Security tests (critical)")
    config.addinivalue_line("markers", "performance: Performance tests (scalability)")
