"""
Hume historical data integration task.
"""

import logging
import statistics
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List

import numpy as np

logger = logging.getLogger(__name__)


def merge_historical_data(
    device_id: str, start_date: datetime, end_date: datetime
) -> Dict:
    """📊 تكامل البيانات التاريخية"""
    logger.info(f"📊 Merging historical data for {device_id}")

    try:
        # Fetch historical data (simulated)
        historical_sessions = _fetch_historical_sessions(
            device_id, start_date, end_date
        )

        if not historical_sessions:
            return {"error": "No historical data found", "sessions": 0}

        # Process and analyze historical data
        processed_data = _process_historical_data(historical_sessions)

        # Generate insights and trends
        insights = _generate_historical_insights(processed_data)

        # Create comprehensive report
        report = {
            "device_id": device_id,
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": (end_date - start_date).days,
            },
            "summary": {
                "total_sessions": len(historical_sessions),
                "most_common_emotion": insights["dominant_emotion"],
                "emotional_stability": insights["stability_score"],
                "trend": insights["trend"],
            },
            "daily_breakdown": processed_data["daily_summaries"],
            "recommendations": insights["recommendations"],
        }

        logger.info(
            f"✅ Historical analysis complete: {len(historical_sessions)} sessions processed"
        )
        return report

    except Exception as e:
        logger.error(f"❌ Historical data merge failed: {e}")
        return {"error": str(e)}


def _fetch_historical_sessions(
    device_id: str, start_date: datetime, end_date: datetime
) -> List[Dict]:
    """جلب الجلسات التاريخية من قاعدة البيانات"""
    # Simulated historical data
    sessions = []
    current_date = start_date

    while current_date <= end_date:
        # Generate 1-3 sessions per day
        num_sessions = np.random.randint(1, 4)

        for i in range(num_sessions):
            session = {
                "timestamp": current_date
                + timedelta(hours=np.random.randint(8, 20)),
                "device_id": device_id,
                "audio_duration": np.random.uniform(5, 30),  # seconds
                "emotions": {
                    "joy": np.random.uniform(0.2, 0.8),
                    "curiosity": np.random.uniform(0.3, 0.7),
                    "excitement": np.random.uniform(0.1, 0.6),
                    "calmness": np.random.uniform(0.2, 0.5),
                },
            }

            # Add dominant emotion
            session["dominant_emotion"] = max(
                session["emotions"], key=session["emotions"].get
            )
            session["confidence"] = session["emotions"][session["dominant_emotion"]]

            sessions.append(session)

            current_date += timedelta(days=1)

    return sessions


def _initialize_daily_summary(summaries: Dict, date_key: str):
    """Initializes a summary dictionary for a given day if it doesn't exist."""
    if date_key not in summaries:
        summaries[date_key] = {
            "sessions": 0,
            "total_duration": 0,
            "emotions": {},
            "dominant_emotions": [],
        }


def _update_daily_summary(day_summary: Dict, session: Dict):
    """Updates a daily summary with data from a single session."""
    day_summary["sessions"] += 1
    day_summary["total_duration"] += session["audio_duration"]
    day_summary["dominant_emotions"].append(session["dominant_emotion"])
    for emotion, score in session["emotions"].items():
        day_summary["emotions"].setdefault(emotion, []).append(score)


def _finalize_daily_summaries(summaries: Dict):
    """Calculates the average emotion scores for each day."""
    for day_data in summaries.values():
        for emotion, scores in day_data["emotions"].items():
            day_data["emotions"][emotion] = statistics.mean(
                scores) if scores else 0


def _process_historical_data(sessions: List[Dict]) -> Dict:
    """معالجة البيانات التاريخية"""
    daily_summaries = {}
    all_emotions = defaultdict(list)

    for session in sessions:
        date_key = session["timestamp"].date().isoformat()
        _initialize_daily_summary(daily_summaries, date_key)
        _update_daily_summary(daily_summaries[date_key], session)

        for emotion, score in session["emotions"].items():
            all_emotions[emotion].append(score)

    _finalize_daily_summaries(daily_summaries)

    overall_emotions = {
        emotion: statistics.mean(scores)
        for emotion, scores in all_emotions.items()
        if scores
    }

    return {
        "daily_summaries": daily_summaries,
        "overall_emotions": overall_emotions,
    }


def _calculate_stability(daily_summaries: Dict) -> float:
    """Calculates the emotional stability score."""
    daily_dominant_emotions = [
        max(day_data["emotions"], key=day_data["emotions"].get)
        for day_data in daily_summaries.values()
        if day_data["emotions"]
    ]
    if not daily_dominant_emotions:
        return 0.5

    most_common_daily = max(
        set(daily_dominant_emotions), key=daily_dominant_emotions.count
    )
    return daily_dominant_emotions.count(most_common_daily) / len(
        daily_dominant_emotions
    )


def _analyze_trend(daily_summaries: Dict) -> str:
    """Analyzes the emotional trend over time."""
    if len(daily_summaries) < 7:
        return "insufficient_data"

    recent_days = list(daily_summaries.values())[-7:]
    early_days = list(daily_summaries.values())[:7]

    recent_joy = statistics.mean(
        [day["emotions"].get("joy", 0) for day in recent_days]
    )
    early_joy = statistics.mean(
        [day["emotions"].get("joy", 0) for day in early_days]
    )

    if recent_joy > early_joy + 0.1:
        return "improving"
    if recent_joy < early_joy - 0.1:
        return "declining"
    return "stable"


def _generate_recommendations_from_insights(
    dominant_emotion: str, stability_score: float, trend: str
) -> List[str]:
    """Generates recommendations based on historical insights."""
    recommendations = []
    if dominant_emotion == "curiosity":
        recommendations.append(
            "Child shows high curiosity - great time for educational activities"
        )
    elif dominant_emotion == "joy":
        recommendations.append(
            "Child is generally happy - maintain current approach"
        )

    if stability_score < 0.5:
        recommendations.append(
            "Emotional patterns vary - monitor for consistency")

    if trend == "improving":
        recommendations.append("Positive emotional trend detected")
    elif trend == "declining":
        recommendations.append("Consider additional emotional support")

    return recommendations


def _generate_historical_insights(processed_data: Dict) -> Dict:
    """توليد الرؤى من البيانات التاريخية"""
    overall_emotions = processed_data["overall_emotions"]
    daily_summaries = processed_data["daily_summaries"]

    dominant_emotion = (
        max(overall_emotions, key=overall_emotions.get)
        if overall_emotions
        else "unknown"
    )
    stability_score = _calculate_stability(daily_summaries)
    trend = _analyze_trend(daily_summaries)
    recommendations = _generate_recommendations_from_insights(
        dominant_emotion, stability_score, trend
    )

    return {
        "dominant_emotion": dominant_emotion,
        "stability_score": stability_score,
        "trend": trend,
        "recommendations": recommendations,
    }
