"""
Chart Generation Service
=======================

Infrastructure service for generating charts and visualizations.
Uses matplotlib, seaborn, and plotly for different chart types.
"""

import base64
import logging
from io import BytesIO
from typing import Any, Dict, List

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns


class ChartGenerationService:
    """Service for generating charts from analytics data"""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        # Set matplotlib backend for server environments
        plt.switch_backend("Agg")

        # Set style
        plt.style.use("seaborn-v0_8-whitegrid")
        sns.set_palette("husl")

    def generate_usage_trend_chart(
        self, daily_data: List[Dict[str, Any]], title: str = "Daily Usage Trend"
    ) -> str:
        """Generate daily usage trend chart"""

        try:
            # Prepare data
            dates = [item["date"] for item in daily_data]
            conversations = [item["conversations"] for item in daily_data]

            plt.figure(figsize=(12, 6))
            plt.plot(dates, conversations, marker="o", linewidth=2, markersize=6)
            plt.title(title, fontsize=16, fontweight="bold")
            plt.xlabel("Date", fontsize=12)
            plt.ylabel("Number of Conversations", fontsize=12)
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)
            plt.tight_layout()

            # Convert to base64
            return self._save_chart_to_base64()

        except Exception as e:
            self.logger.error(f"Error generating usage trend chart: {e}")
            return ""

    def generate_topic_distribution_chart(
        self, topics_frequency: Dict[str, int], title: str = "Topics Discussed"
    ) -> str:
        """Generate pie chart for topic distribution"""

        try:
            if not topics_frequency:
                return ""

            topics = list(topics_frequency.keys())
            counts = list(topics_frequency.values())

            plt.figure(figsize=(10, 8))
            colors = plt.cm.Set3(np.linspace(0, 1, len(topics)))

            plt.pie(
                counts, labels=topics, autopct="%1.1f%%", colors=colors, startangle=90
            )
            plt.title(title, fontsize=16, fontweight="bold")
            plt.axis("equal")

            return self._save_chart_to_base64()

        except Exception as e:
            self.logger.error(f"Error generating topic distribution chart: {e}")
            return ""

    def generate_sentiment_chart(
        self,
        sentiment_breakdown: Dict[str, float],
        title: str = "Conversation Sentiment",
    ) -> str:
        """Generate bar chart for sentiment breakdown"""

        try:
            sentiments = list(sentiment_breakdown.keys())
            scores = list(sentiment_breakdown.values())

            plt.figure(figsize=(8, 6))
            colors = ["#2ecc71", "#f39c12", "#e74c3c"]  # Green, orange, red

            bars = plt.bar(sentiments, scores, color=colors[: len(sentiments)])
            plt.title(title, fontsize=16, fontweight="bold")
            plt.ylabel("Average Score", fontsize=12)
            plt.ylim(0, 1)

            # Add value labels on bars
            for bar, score in zip(bars, scores):
                plt.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 0.01,
                    f"{score:.2f}",
                    ha="center",
                    va="bottom",
                    fontweight="bold",
                )

            plt.tight_layout()

            return self._save_chart_to_base64()

        except Exception as e:
            self.logger.error(f"Error generating sentiment chart: {e}")
            return ""

    def generate_learning_progress_chart(
        self, progress_data: Dict[str, float], title: str = "Learning Progress"
    ) -> str:
        """Generate radar chart for learning progress"""

        try:
            categories = list(progress_data.keys())
            values = list(progress_data.values())

            # Number of variables
            N = len(categories)

            # Compute angles for each axis
            angles = [n / float(N) * 2 * np.pi for n in range(N)]
            angles += angles[:1]  # Complete the circle

            # Add first value to complete the circle
            values += values[:1]

            plt.figure(figsize=(8, 8))
            ax = plt.subplot(111, projection="polar")

            # Plot
            ax.plot(angles, values, "o-", linewidth=2, markersize=6)
            ax.fill(angles, values, alpha=0.25)

            # Add labels
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(categories)
            ax.set_ylim(0, 100)

            plt.title(title, fontsize=16, fontweight="bold", pad=20)

            return self._save_chart_to_base64()

        except Exception as e:
            self.logger.error(f"Error generating learning progress chart: {e}")
            return ""

    def generate_weekly_comparison_chart(
        self,
        weekly_data: List[Dict[str, Any]],
        metric: str = "conversations",
        title: str = "Weekly Comparison",
    ) -> str:
        """Generate weekly comparison chart"""

        try:
            weeks = [f"Week {i+1}" for i in range(len(weekly_data))]
            values = [
                week_data["analytics"].get(metric, 0) for week_data in weekly_data
            ]

            plt.figure(figsize=(10, 6))
            bars = plt.bar(weeks, values, color="skyblue", edgecolor="navy", alpha=0.7)

            plt.title(title, fontsize=16, fontweight="bold")
            plt.ylabel(metric.replace("_", " ").title(), fontsize=12)

            # Add value labels on bars
            for bar, value in zip(bars, values):
                plt.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + max(values) * 0.01,
                    f"{value:.1f}",
                    ha="center",
                    va="bottom",
                    fontweight="bold",
                )

            plt.tight_layout()

            return self._save_chart_to_base64()

        except Exception as e:
            self.logger.error(f"Error generating weekly comparison chart: {e}")
            return ""

    def generate_time_distribution_chart(
        self, peak_hours: List[int], title: str = "Usage by Time of Day"
    ) -> str:
        """Generate chart showing usage distribution by hour"""

        try:
            # Create hourly usage data
            hours = list(range(24))
            usage_counts = [peak_hours.count(hour) for hour in hours]

            plt.figure(figsize=(12, 6))
            bars = plt.bar(hours, usage_counts, color="lightcoral", alpha=0.7)

            plt.title(title, fontsize=16, fontweight="bold")
            plt.xlabel("Hour of Day", fontsize=12)
            plt.ylabel("Usage Frequency", fontsize=12)
            plt.xticks(range(0, 24, 2))
            plt.grid(True, alpha=0.3)

            # Highlight peak hours
            max_usage = max(usage_counts) if usage_counts else 0
            for i, (hour, count) in enumerate(zip(hours, usage_counts)):
                if count == max_usage and count > 0:
                    bars[i].set_color("darkred")

            plt.tight_layout()

            return self._save_chart_to_base64()

        except Exception as e:
            self.logger.error(f"Error generating time distribution chart: {e}")
            return ""

    def _save_chart_to_base64(self) -> str:
        """Save current matplotlib chart to base64 string"""

        try:
            buffer = BytesIO()
            plt.savefig(buffer, format="png", dpi=150, bbox_inches="tight")
            buffer.seek(0)

            # Convert to base64
            chart_data = base64.b64encode(buffer.read()).decode()

            # Clean up
            buffer.close()
            plt.close()

            return chart_data

        except Exception as e:
            self.logger.error(f"Error saving chart to base64: {e}")
            plt.close()  # Ensure cleanup
            return ""

    def generate_comprehensive_dashboard_charts(
        self, analytics_data: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generate all charts for dashboard"""

        charts = {}

        try:
            # Usage trend chart
            if "daily_usage" in analytics_data:
                charts["usage_trend"] = self.generate_usage_trend_chart(
                    analytics_data["daily_usage"]
                )

            # Topic distribution
            if "topics_frequency" in analytics_data:
                charts["topic_distribution"] = self.generate_topic_distribution_chart(
                    analytics_data["topics_frequency"]
                )

            # Sentiment breakdown
            if "sentiment_breakdown" in analytics_data:
                charts["sentiment_overview"] = self.generate_sentiment_chart(
                    analytics_data["sentiment_breakdown"]
                )

            # Learning progress
            if "learning_progress" in analytics_data:
                progress_data = analytics_data["learning_progress"]
                if isinstance(progress_data, dict):
                    charts["learning_progress"] = self.generate_learning_progress_chart(
                        progress_data
                    )

            # Time distribution
            if "peak_usage_hours" in analytics_data:
                charts["time_distribution"] = self.generate_time_distribution_chart(
                    analytics_data["peak_usage_hours"]
                )

            self.logger.info(f"Generated {len(charts)} charts successfully")

        except Exception as e:
            self.logger.error(f"Error generating comprehensive charts: {e}")

        return charts
