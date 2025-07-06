from datetime import datetime, timedelta
from typing import Any, Dict, List

import numpy as np
import structlog

logger = structlog.get_logger()


class EmotionAnalyticsEngine:
    """Advanced emotion analytics with machine learning insights"""

    def __init__(self):
        self.emotion_history = []
        self.patterns = {}
        self.predictions = {}
        self.setup_plotly()

    def setup_plotly(self) -> Any:
        """Setup Plotly for advanced visualization"""
        try:
            import plotly.express as px
            import plotly.figure_factory as ff
            import plotly.graph_objects as go

            self.plotly_available = True
            self.go = go
            self.px = px
            self.ff = ff

            logger.info("Plotly analytics engine initialized successfully")

        except ImportError:
            self.plotly_available = False
            logger.warning(
                "Plotly not available - install with: pip install plotly")

    def add_emotion_data(
        self,
        emotion_data: dict = None,
        emotion: str = None,
        confidence: float = None,
        metadata: dict = None,
    ) -> None:
        """Add new emotion data point"""
        entry = {
            "emotion": emotion,
            "confidence": confidence,
            "timestamp": datetime.now(),
            "metadata": metadata or {},
        }

        self.emotion_history.append(entry)

        # Keep only last 1000 entries for performance
        if len(self.emotion_history) > 1000:
            self.emotion_history.pop(0)

        # Trigger pattern analysis
        self.analyze_patterns()

    def analyze_patterns(self) -> Any:
        """Analyze emotion patterns for insights"""
        if len(self.emotion_history) < 10:
            return

        # Analyze emotion transitions
        transitions = {}
        for i in range(1, len(self.emotion_history)):
            prev_emotion = self.emotion_history[i - 1]["emotion"]
            curr_emotion = self.emotion_history[i]["emotion"]

            transition = f"{prev_emotion} -> {curr_emotion}"
            transitions[transition] = transitions.get(transition, 0) + 1

        self.patterns["transitions"] = transitions

        # Analyze time-based patterns
        hourly_emotions = {}
        for entry in self.emotion_history[-100:]:  # Last 100 entries
            hour = entry["timestamp"].hour
            emotion = entry["emotion"]

            if hour not in hourly_emotions:
                hourly_emotions[hour] = {}

            hourly_emotions[hour][emotion] = hourly_emotions[hour].get(
                emotion, 0) + 1

        self.patterns["hourly"] = hourly_emotions

    def _filter_recent_emotion_data(self, hours: int) -> List[Dict]:
        """Filters emotion data for a given time range in hours."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            entry for entry in self.emotion_history if entry["timestamp"] >= cutoff_time]

    def _prepare_timeline_data(
            self, recent_data: List[Dict]) -> Dict[str, List]:
        """Prepares data for timeline chart creation."""
        timestamps = [entry["timestamp"] for entry in recent_data]
        emotions = [entry["emotion"] for entry in recent_data]
        confidences = [entry["confidence"] for entry in recent_data]
        return {
            "timestamps": timestamps,
            "emotions": emotions,
            "confidences": confidences,
        }

    def _add_emotion_traces_to_fig(
        self, fig: Any, timeline_data: Dict[str, List]
    ) -> None:
        """Adds emotion traces to the Plotly figure."""
        emotion_colors = {
            "happy": "#4CAF50",
            "excited": "#FF9800",
            "calm": "#2196F3",
            "curious": "#9C27B0",
            "frustrated": "#F44336",
            "sad": "#607D8B",
            "angry": "#E91E63",
            "surprised": "#FFEB3B",
            "neutral": "#9E9E9E",
        }
        unique_emotions = list(set(timeline_data["emotions"]))

        for emotion in unique_emotions:
            emotion_indices = [
                i for i, e in enumerate(
                    timeline_data["emotions"]) if e == emotion]
            emotion_times = [timeline_data["timestamps"][i]
                             for i in emotion_indices]
            emotion_conf = [timeline_data["confidences"][i]
                            for i in emotion_indices]

            fig.add_trace(
                self.go.Scatter(
                    x=emotion_times,
                    y=emotion_conf,
                    mode="lines+markers",
                    name=emotion.title(),
                    line=dict(
                        color=emotion_colors.get(
                            emotion,
                            "#666666"),
                        width=3),
                    marker=dict(
                        size=10,
                        opacity=0.8),
                    hovertemplate=f"<b>{emotion.title()}</b><br>Confidence: %{{y:.1%}}<br>Time: %{{x}}<extra></extra>",
                ))

    def _configure_timeline_chart_layout(self, fig: Any, hours: int) -> None:
        """Configures the layout for the timeline chart."""
        fig.update_layout(
            title={
                "text": f"Emotion Timeline - Last {hours} Hours",
                "x": 0.5,
                "xanchor": "center",
                "font": {"size": 18},
            },
            xaxis_title="Time",
            yaxis_title="Confidence Level",
            yaxis=dict(tickformat=".0%"),
            hovermode="x unified",
            template="plotly_white",
            height=400,
            margin=dict(l=60, r=60, t=80, b=60),
        )

    def create_emotion_timeline_chart(self, hours: int = 6) -> Any:
        """Create interactive emotion timeline chart"""
        if not self.plotly_available:
            return None

        recent_data = self._filter_recent_emotion_data(hours)
        if not recent_data:
            return None

        timeline_data = self._prepare_timeline_data(recent_data)

        fig = self.go.Figure()
        self._add_emotion_traces_to_fig(fig, timeline_data)
        self._configure_timeline_chart_layout(fig, hours)

        return fig

    def _count_recent_emotions(self, num_entries: int = 50) -> Dict[str, int]:
        """Counts emotions from a specified number of recent entries."""
        recent_data = self.emotion_history[-num_entries:]
        emotion_counts = {}
        for entry in recent_data:
            emotion = entry["emotion"]
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        return emotion_counts

    def _create_distribution_figure(
            self, emotion_counts: Dict[str, int]) -> Any:
        """Creates the distribution pie chart figure."""
        return self.go.Figure(
            data=[
                self.go.Pie(
                    labels=list(emotion_counts.keys()),
                    values=list(emotion_counts.values()),
                    hole=0.4,
                    textinfo="label+percent",
                    textfont_size=14,
                    marker=dict(
                        colors=[
                            "#FF6B6B",
                            "#4ECDC4",
                            "#45B7D1",
                            "#96CEB4",
                            "#FFEAA7",
                            "#DDA0DD",
                            "#98D8C8",
                            "#F7DC6F",
                        ],
                        line=dict(color="#FFFFFF", width=2),
                    ),
                )
            ]
        )

    def _configure_distribution_chart_layout(self, fig: Any) -> None:
        """Configures the layout for the distribution chart."""
        fig.update_layout(
            title={
                "text": "Emotion Distribution (Recent Activity)",
                "x": 0.5,
                "xanchor": "center",
                "font": {"size": 16},
            },
            template="plotly_white",
            height=350,
            margin=dict(l=60, r=60, t=80, b=60),
        )

    def create_emotion_distribution_chart(self) -> Any:
        """Create emotion distribution pie chart"""
        if not self.plotly_available or not self.emotion_history:
            return None

        emotion_counts = self._count_recent_emotions()
        if not emotion_counts:
            return None

        fig = self._create_distribution_figure(emotion_counts)
        self._configure_distribution_chart_layout(fig)

        return fig

    def _prepare_heatmap_data(self, num_entries: int = 200) -> Dict[str, Any]:
        """Prepares data for the emotion intensity heatmap."""
        hours = list(range(24))
        emotions = [
            "happy",
            "excited",
            "calm",
            "curious",
            "frustrated",
            "sad",
            "angry"]
        intensity_matrix = np.zeros((len(emotions), len(hours)))

        for entry in self.emotion_history[-num_entries:]:
            hour = entry["timestamp"].hour
            emotion = entry["emotion"]
            confidence = entry["confidence"]

            if emotion in emotions:
                emotion_idx = emotions.index(emotion)
                intensity_matrix[emotion_idx][hour] += confidence

        max_val = np.max(intensity_matrix) if np.max(
            intensity_matrix) > 0 else 1
        intensity_matrix /= max_val

        return {
            "matrix": intensity_matrix,
            "hours": hours,
            "emotions": emotions}

    def _create_heatmap_figure(self, heatmap_data: Dict[str, Any]) -> Any:
        """Creates the emotion intensity heatmap figure."""
        return self.go.Figure(
            data=self.go.Heatmap(
                z=heatmap_data["matrix"],
                x=[f"{h:02d}:00" for h in heatmap_data["hours"]],
                y=[e.title() for e in heatmap_data["emotions"]],
                colorscale="Viridis",
                hoverongaps=False,
                hovertemplate="Hour: %{x}<br>Emotion: %{y}<br>Intensity: %{z:.2f}<extra></extra>",
            )
        )

    def _configure_heatmap_layout(self, fig: Any) -> None:
        """Configures the layout for the emotion intensity heatmap."""
        fig.update_layout(
            title={
                "text": "Emotion Intensity Heatmap by Hour",
                "x": 0.5,
                "xanchor": "center",
                "font": {"size": 16},
            },
            xaxis_title="Hour of Day",
            yaxis_title="Emotion Type",
            template="plotly_white",
            height=400,
            margin=dict(l=100, r=60, t=80, b=60),
        )

    def create_emotion_heatmap(self) -> Any:
        """Create emotion intensity heatmap by hour"""
        if not self.plotly_available or not self.emotion_history:
            return None

        heatmap_data = self._prepare_heatmap_data()

        fig = self._create_heatmap_figure(heatmap_data)
        self._configure_heatmap_layout(fig)

        return fig

    def _calculate_dominant_emotion(self, recent_emotions: List[Dict]) -> str:
        """Calculate the dominant emotion from a list of recent emotions."""
        if not recent_emotions:
            return "unknown"
        emotion_counts = {}
        for entry in recent_emotions:
            emotion = entry["emotion"]
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        return max(emotion_counts.items(), key=lambda x: x[1])[0]

    def _detect_emotion_trend(self, recent_emotions: List[Dict]) -> str:
        """Detect the trend of emotions."""
        if len(recent_emotions) < 10:
            return "stable"

        first_half = recent_emotions[: len(recent_emotions) // 2]
        second_half = recent_emotions[len(recent_emotions) // 2:]

        first_avg_positivity = sum(
            1 for e in first_half if e["emotion"] in [
                "happy", "excited", "calm"]) / len(first_half)
        second_avg_positivity = sum(
            1 for e in second_half if e["emotion"] in [
                "happy", "excited", "calm"]) / len(second_half)

        if second_avg_positivity > first_avg_positivity + 0.2:
            return "improving"
        elif second_avg_positivity < first_avg_positivity - 0.2:
            return "declining"
        return "stable"

    def get_emotion_insights(self) -> Dict[str, Any]:
        """Get AI-powered emotion insights."""
        if len(self.emotion_history) < 5:
            return {"status": "insufficient_data"}

        recent_emotions = self.emotion_history[-20:]
        dominant_emotion = self._calculate_dominant_emotion(recent_emotions)
        avg_confidence = sum(e["confidence"] for e in recent_emotions) / len(
            recent_emotions
        )
        trend = self._detect_emotion_trend(recent_emotions)

        return {
            "status": "ready",
            "dominant_emotion": dominant_emotion,
            "average_confidence": avg_confidence,
            "trend": trend,
            "total_interactions": len(self.emotion_history),
            "patterns_detected": len(self.patterns.get("transitions", {})),
        }
