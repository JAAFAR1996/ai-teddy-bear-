#!/usr/bin/env python3
"""
📄 GraphQL Cursor-based Pagination
Lead Architect: جعفر أديب (Jaafar Adeeb)
High-performance cursor pagination for GraphQL
"""

import base64
import json
from typing import List, Dict, Any, Optional, TypeVar, Generic
from dataclasses import dataclass
from datetime import datetime
import structlog

logger = structlog.get_logger()
T = TypeVar('T')


@dataclass
class PageInfo:
    """GraphQL Connection PageInfo"""
    has_next_page: bool
    has_previous_page: bool
    start_cursor: Optional[str] = None
    end_cursor: Optional[str] = None
    total_count: Optional[int] = None


@dataclass
class Edge(Generic[T]):
    """GraphQL Connection Edge"""
    node: T
    cursor: str


@dataclass
class Connection(Generic[T]):
    """GraphQL Connection"""
    edges: List[Edge[T]]
    page_info: PageInfo
    total_count: Optional[int] = None


def encode_cursor(offset: int, timestamp: str = None, **kwargs) -> str:
    """Encode cursor for pagination"""
    cursor_data = {"offset": offset, "timestamp": timestamp, **kwargs}
    cursor_json = json.dumps(cursor_data, sort_keys=True)
    return base64.b64encode(cursor_json.encode()).decode()


def decode_cursor(encoded_cursor: str) -> Dict[str, Any]:
    """Decode pagination cursor"""
    try:
        cursor_json = base64.b64decode(encoded_cursor.encode()).decode()
        return json.loads(cursor_json)
    except Exception as e:
        return {"offset": 0}


class CursorPaginator:
    """
    🏗️ Cursor-based Paginator
    High-performance pagination with caching support
    """
    
    def __init__(self, repository, cache_client=None):
        self.repository = repository
        self.cache_client = cache_client
        self.default_limit = 20
        self.max_limit = 100
    
    async def paginate(
        self,
        first: Optional[int] = None,
        after: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        sort_field: str = "created_at",
        sort_direction: str = "DESC"
    ) -> Connection[Dict[str, Any]]:
        """
        Paginate results with cursor-based pagination
        """
        # Validate and set limit
        limit = min(first or self.default_limit, self.max_limit)
        
        # Decode cursor
        cursor_data = decode_cursor(after) if after else {"offset": 0}
        offset = cursor_data.get("offset", 0)
        
        # Fetch extra item to check for next page
        items = await self.repository.get_paginated(
            offset=offset,
            limit=limit + 1,
            filters=filters or {},
            sort_field=sort_field,
            sort_direction=sort_direction
        )
        
        # Check if there are more items
        has_next_page = len(items) > limit
        if has_next_page:
            items = items[:limit]
        
        # Create edges
        edges = []
        for i, item in enumerate(items):
            cursor = encode_cursor(
                offset=offset + i + 1,
                timestamp=getattr(item, sort_field, datetime.utcnow()).isoformat()
            )
            edges.append(Edge(node=self._serialize_item(item), cursor=cursor))
        
        # Create page info
        page_info = PageInfo(
            has_next_page=has_next_page,
            has_previous_page=offset > 0,
            start_cursor=edges[0].cursor if edges else None,
            end_cursor=edges[-1].cursor if edges else None
        )
        
        # Get total count if needed
        total_count = await self.repository.count(filters or {}) if filters else None
        
        return Connection(
            edges=edges,
            page_info=page_info,
            total_count=total_count
        )
    
    def _serialize_item(self, item) -> Dict[str, Any]:
        """Serialize item for GraphQL response"""
        if hasattr(item, '__dict__'):
            return {k: v for k, v in item.__dict__.items() if not k.startswith('_')}
        return item 