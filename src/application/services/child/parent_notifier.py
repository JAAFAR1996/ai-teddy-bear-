from typing import Any, Dict
import asyncio
import time
import structlog

from .enhanced_child_interaction_service import ContentAnalysisResult, ChildSession

logger = structlog.get_logger(__name__)


class ParentNotifier:
    """Handles sending notifications to parents."""

    async def handle_notification(
        self,
        child_id: str,
        content_analysis: "ContentAnalysisResult",
        session: "ChildSession",
    ) -> bool:
        """Handle parent notifications based on content analysis."""
        try:
            if content_analysis.parent_notification_required:
                notification_data = {
                    "child_id": child_id,
                    "child_name": session.child_name,
                    "risk_level": content_analysis.risk_level.value,
                    "violations": [v.description for v in content_analysis.violations],
                    "timestamp": time.time(),
                    "recommendations": content_analysis.safety_recommendations,
                }
                logger.warning("📧 Parent notification required",
                               child_id=child_id, notification_data=notification_data)
                await asyncio.sleep(0.05)  # Simulate sending notification
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Parent notification failed: {e}")
            return False
