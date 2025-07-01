"""
💾 Persistence Adapters - AI Teddy Bear
======================================

Outbound adapters for data persistence.
These adapters implement repository ports using specific
database technologies while keeping the domain independent.

Supported persistence technologies:
- PostgreSQL for transactional data
- Redis for caching
- S3 for file storage
- MongoDB for analytics data

Following Repository Pattern:
- Implement repository ports from core
- Handle data mapping between domain and persistence models
- Manage transactions and connections
- Provide query optimization
"""

from .mongodb import MongoAnalyticsRepository, MongoLogRepository
from .postgresql import (PostgreSQLChildRepository,
                         PostgreSQLConversationRepository,
                         PostgreSQLEventStore)
from .redis import RedisCacheRepository, RedisSessionRepository
from .s3 import S3AudioFileRepository, S3BackupRepository

__all__ = [
    # PostgreSQL Adapters
    "PostgreSQLChildRepository",
    "PostgreSQLConversationRepository",
    "PostgreSQLEventStore",
    # Redis Adapters
    "RedisCacheRepository",
    "RedisSessionRepository",
    # S3 Adapters
    "S3AudioFileRepository",
    "S3BackupRepository",
    # MongoDB Adapters
    "MongoAnalyticsRepository",
    "MongoLogRepository",
]
