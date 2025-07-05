from typing import List
from datetime import datetime, timedelta

try:
    import strawberry
except ImportError:
    class strawberry:
        def enum(x): return x
        type = lambda *args, **kwargs: (lambda x: x)
        federation = type("federation", (), {
                          "type": type, "field": lambda **kwargs: None})()
        field = lambda *args, **kwargs: None
        ID = type("ID", (), {})

from .service_resolvers import Child, Conversation, RiskLevel, SafetyProfile, RiskAssessment, SafetyCheck


@strawberry.federation.type(extend=True)
class Child:
    id: strawberry.ID = strawberry.federation.field(external=True)

    @strawberry.field
    async def safety_profile(self) -> "SafetyProfile":
        return SafetyProfile(risk_level=RiskLevel.LOW, safety_score=0.92, last_safety_check=datetime.now() - timedelta(hours=1))

    @strawberry.field
    async def risk_assessment(self) -> "RiskAssessment":
        return RiskAssessment(overall_risk=0.15, last_assessed=datetime.now() - timedelta(hours=12))


@strawberry.federation.type(extend=True)
class Conversation:
    id: strawberry.ID = strawberry.federation.field(external=True)

    @strawberry.field
    async def safety_check(self) -> "SafetyCheck":
        return SafetyCheck(passed=True, score=0.94, timestamp=datetime.now(), review_required=False)


class SafetyServiceResolvers:
    @staticmethod
    async def get_safety_profile(child_id: strawberry.ID) -> "SafetyProfile":
        return SafetyProfile(risk_level=RiskLevel.LOW, safety_score=0.89, last_safety_check=datetime.now())
