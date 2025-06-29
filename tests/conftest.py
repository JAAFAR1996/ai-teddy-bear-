import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import uuid

class ChildProfile:
    """Mock child profile for testing"""
    def __init__(self, name: str, age: int):
        self.id = str(uuid.uuid4())
        self.name = name
        self.age = age

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def async_client():
    """Create async HTTP client for testing"""
    # Mock FastAPI app would be imported here
    # app = create_app()
    async with AsyncClient(base_url="http://test") as client:
        yield client

@pytest.fixture
async def db_session():
    """Create database session for testing"""
    # Mock database setup
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async_session = sessionmaker(engine, class_=AsyncSession)
    
    async with async_session() as session:
        yield session

@pytest.fixture
def test_child():
    """Create test child profile"""
    return ChildProfile(name="Ahmed", age=6)

@pytest.fixture
def active_session():
    """Create active session ID for testing"""
    return str(uuid.uuid4())