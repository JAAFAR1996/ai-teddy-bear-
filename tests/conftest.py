#!/usr/bin/env python3
"""
📝 إعدادات pytest للمشروع
حل مشاكل imports والpaths
"""

import sys
import os
import logging
from pathlib import Path

# إضافة مجلد src إلى Python path
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))
sys.path.insert(0, str(project_root))

# إعداد logging للاختبارات
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# تعطيل warnings غير المهمة
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=PendingDeprecationWarning)

# Mock للمكتبات المفقودة
try:
    import torch
except ImportError:
    # Mock torch للاختبارات
    import sys
    from unittest.mock import MagicMock
    sys.modules['torch'] = MagicMock()
    sys.modules['torch.nn'] = MagicMock()
    sys.modules['torchaudio'] = MagicMock()

try:
    import pyaudio
except ImportError:
    import sys
    from unittest.mock import MagicMock
    sys.modules['pyaudio'] = MagicMock()

try:
    import redis
except ImportError:
    import sys
    from unittest.mock import MagicMock
    sys.modules['redis'] = MagicMock()

# إعداد متغيرات البيئة للاختبارات
os.environ.setdefault('TESTING', 'true')
os.environ.setdefault('LOG_LEVEL', 'INFO')

import asyncio
import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker


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
