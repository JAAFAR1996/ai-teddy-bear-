"""
Analytics component for the API Gateway.
"""
import logging
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Any, Dict, List

from .models import RequestAnalytics, ThreatLevel

logger = logging.getLogger(__name__)


class AnalyticsCollectorMixin:
    """A mixin providing request analytics and monitoring capabilities."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request_analytics: deque = deque(maxlen=10000)

    async def record_request_analytics(
        self, request, response, response_time: float, threat_level: ThreatLevel, blocked: bool
    ):
        """Records the analytics for a single processed request."""
        analytics_data = RequestAnalytics(
            timestamp=datetime.utcnow(),
            ip_address=self._get_client_ip(request),
            user_id=await self._extract_user_id(request),
            endpoint=str(request.url.path),
            method=request.method,
            response_time=response_time,
            status_code=response.status_code,
            user_agent=request.headers.get("user-agent", "unknown"),
            threat_level=threat_level,
            blocked=blocked,
        )
        self.request_analytics.append(analytics_data)

    async def get_analytics_summary(self) -> Dict[str, Any]:
        """Provides a summary of analytics for a recent time window (e.g., the last hour)."""
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        recent_requests = [
            r for r in self.request_analytics if r.timestamp > one_hour_ago]

        total = len(recent_requests)
        if total == 0:
            return {"total_requests_last_hour": 0}

        return {
            "total_requests_last_hour": total,
            "unique_ips_last_hour": len({r.ip_address for r in recent_requests}),
            "blocked_requests_last_hour": len([r for r in recent_requests if r.blocked]),
            "avg_response_time_ms": (sum(r.response_time for r in recent_requests) / total) * 1000,
            "top_endpoints": self._get_top_endpoints(recent_requests, 5),
            "threat_level_counts": self._get_threat_level_counts(recent_requests),
        }

    def _get_top_endpoints(self, requests: List[RequestAnalytics], limit: int) -> List[Dict[str, Any]]:
        """Calculates the top N most frequently requested endpoints."""
        counts = defaultdict(int)
        for r in requests:
            counts[r.endpoint] += 1

        sorted_endpoints = sorted(
            counts.items(), key=lambda item: item[1], reverse=True)
        return [{"endpoint": ep, "count": ct} for ep, ct in sorted_endpoints[:limit]]

    def _get_threat_level_counts(self, requests: List[RequestAnalytics]) -> Dict[str, int]:
        """Counts the number of requests for each threat level."""
        counts = defaultdict(int)
        for r in requests:
            counts[r.threat_level.value] += 1
        return dict(counts)

    # Placeholders that the main gateway class will implement
    def _get_client_ip(self, request) -> str: raise NotImplementedError
    async def _extract_user_id(self, request) -> str: raise NotImplementedError
