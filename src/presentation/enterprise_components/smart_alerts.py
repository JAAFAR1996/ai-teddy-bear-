from datetime import datetime, timedelta
from typing import Dict, List

import structlog

logger = structlog.get_logger()


class SmartAlertSystem:
    """Intelligent alert system for parents"""

    def __init__(self):
        self.alert_rules = self.setup_alert_rules()
        self.alerts_history = []
        self.sensitivity = 1.0
        self.enabled = True

    def setup_alert_rules(self) -> Dict[str, Dict]:
        """Setup predefined alert rules"""
        return {
            "negative_emotion_streak": {
                "description": "Child showing persistent negative emotions",
                "threshold": 3,
                "timeframe": 300,  # 5 minutes
                "priority": "high",
                "emoji": "😟",
            },
            "sudden_mood_drop": {
                "description": "Sudden significant mood change detected",
                "threshold": 0.6,  # 60% confidence drop
                "priority": "medium",
                "emoji": "📉",
            },
            "extended_silence": {
                "description": "Child has been unusually quiet",
                "threshold": 1800,  # 30 minutes
                "priority": "low",
                "emoji": "🤫",
            },
            "high_frustration": {
                "description": "High frustration levels detected",
                "threshold": 0.8,  # 80% confidence
                "priority": "high",
                "emoji": "😤",
            },
            "learning_difficulty": {
                "description": "Child may be struggling with learning content",
                "threshold": 5,  # 5 confusion signals
                "priority": "medium",
                "emoji": "🤔",
            },
        }

    def _check_negative_emotion_streak(
        self, emotion_history: List[Dict], new_alerts: List[Dict]
    ) -> None:
        """Checks for a streak of negative emotions."""
        negative_emotions = ["sad", "angry", "frustrated", "confused"]
        recent_negative = [e for e in emotion_history[-10:]
                           if e["emotion"] in negative_emotions]

        if (
            len(recent_negative)
            >= self.alert_rules["negative_emotion_streak"]["threshold"]
        ):
            alert = self.create_alert(
                "negative_emotion_streak",
                f"Child has shown {len(recent_negative)} negative emotions recently",
                {"emotions": recent_negative},
            )
            new_alerts.append(alert)

    def _check_sudden_mood_drop(
        self, emotion_history: List[Dict], new_alerts: List[Dict]
    ) -> None:
        """Checks for a sudden drop in mood."""
        if len(emotion_history) < 2:
            return

        recent_confidence = emotion_history[-1]["confidence"]
        previous_confidence = emotion_history[-2]["confidence"]

        if (previous_confidence - recent_confidence) > self.alert_rules[
            "sudden_mood_drop"
        ]["threshold"]:
            alert = self.create_alert(
                "sudden_mood_drop",
                f"Confidence dropped from {previous_confidence:.1%} to {recent_confidence:.1%}",
                {"previous": previous_confidence, "current": recent_confidence},
            )
            new_alerts.append(alert)

    def _check_high_frustration(
        self, emotion_history: List[Dict], new_alerts: List[Dict]
    ) -> None:
        """Checks for high frustration levels."""
        recent_frustration = [
            e
            for e in emotion_history[-5:]
            if e["emotion"] == "frustrated"
            and e["confidence"] > self.alert_rules["high_frustration"]["threshold"]
        ]

        if recent_frustration:
            alert = self.create_alert(
                "high_frustration",
                f"High frustration level detected: {recent_frustration[-1]['confidence']:.1%}",
                {"confidence": recent_frustration[-1]["confidence"]},
            )
            new_alerts.append(alert)

    ALERT_CHECKERS = {
        "negative_emotion_streak": _check_negative_emotion_streak,
        "sudden_mood_drop": _check_sudden_mood_drop,
        "high_frustration": _check_high_frustration,
    }

    def process_emotion_data(self, emotion_history: List[Dict]) -> List[Dict]:
        """Process emotion data and generate alerts using a dispatch table."""
        if not self.enabled or not emotion_history:
            return []

        new_alerts = []
        for alert_type, checker_func in self.ALERT_CHECKERS.items():
            # The checker function is called with `self` to provide its context
            checker_func(self, emotion_history, new_alerts)

        return new_alerts

    def create_alert(self, alert_type: str, message: str, data: Dict) -> Dict:
        """Create a formatted alert"""
        rule = self.alert_rules.get(alert_type, {})

        alert = {
            "type": alert_type,
            "message": message,
            "data": data,
            "timestamp": datetime.now(),
            "priority": rule.get("priority", "medium"),
            "emoji": rule.get("emoji", "⚠️"),
            "description": rule.get("description", ""),
            "id": len(self.alerts_history) + 1,
        }

        self.alerts_history.append(alert)

        # Keep only last 100 alerts
        if len(self.alerts_history) > 100:
            self.alerts_history.pop(0)

        logger.info(
            "Smart alert generated",
            type=alert_type,
            priority=alert["priority"])

        return alert

    def get_recent_alerts(self, hours: int = 24) -> List[Dict]:
        """Get alerts from specified time period"""
        cutoff_time = datetime.now() - timedelta(hours=hours)

        return [
            alert for alert in self.alerts_history if alert["timestamp"] >= cutoff_time]

    def set_sensitivity(self, level: float) -> None:
        """Set alert sensitivity (0.1 to 2.0)"""
        self.sensitivity = max(0.1, min(2.0, level))

        # Adjust thresholds based on sensitivity
        for rule_name, rule in self.alert_rules.items():
            if "threshold" in rule:
                if rule_name in [
                    "negative_emotion_streak",
                        "learning_difficulty"]:
                    # For count-based thresholds, adjust inversely
                    rule["threshold"] = max(
                        1, int(rule["threshold"] / self.sensitivity)
                    )
                else:
                    # For ratio-based thresholds, adjust directly
                    rule["threshold"] = rule["threshold"] * self.sensitivity

        logger.info("Alert sensitivity updated", level=self.sensitivity)
