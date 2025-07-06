"""
Expose public components of the SQLite persistence layer.
"""

from .sqlite_base import BaseSQLiteRepository, DatabaseError

__all__ = [
    "BaseSQLiteRepository",
    "DatabaseError",
]
