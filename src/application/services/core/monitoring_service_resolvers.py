from typing import List
from datetime import datetime, timedelta

try:
    import strawberry
except ImportError:
    class strawberry:
        type = lambda *args, **kwargs: (lambda x: x)
        federation = type("federation", (), {"type": type, "field": lambda **kwargs: None})()
        field = lambda *args, **kwargs: None
        ID = type("ID", (), {})

from .service_resolvers import Child, Conversation, UsageStatistics, HealthMetrics, PerformanceMetrics


@strawberry.federation.type(extend=True)
class Child:
    id: strawberry.ID = strawberry.federation.field(external=True)

    @strawberry.field
    async def usage(self) -> "UsageStatistics":
        return UsageStatistics(total_session_time=45, daily_usage=25, weekly_usage=180)

    @strawberry.field
    async def health_metrics(self) -> "HealthMetrics":
        return HealthMetrics(overall_score=0.82, emotional_wellbeing=0.88, social_development=0.76, cognitive_growth=0.85, last_assessment=datetime.now() - timedelta(hours=6))


@strawberry.federation.type(extend=True)
class Conversation:
    id: strawberry.ID = strawberry.federation.field(external=True)

    @strawberry.field
    async def performance(self) -> "PerformanceMetrics":
        return PerformanceMetrics(latency=250.5, throughput=95.2, error_rate=0.02, cache_hit_rate=0.78, timestamp=datetime.now())


class MonitoringServiceResolvers:
    @staticmethod
    async def get_usage_statistics(child_id: strawberry.ID, period: str) -> "UsageStatistics":
        return UsageStatistics(total_session_time=120, daily_usage=35, weekly_usage=245)
