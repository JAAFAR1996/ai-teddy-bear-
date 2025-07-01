"""
Chart Generation Infrastructure
Handles chart creation using matplotlib and seaborn
"""

import base64
import io
import logging
from typing import Dict

from src.domain.reporting.models import ChildProgress, EmotionDistribution

# Optional imports for chart generation
try:
    import matplotlib.pyplot as plt
    import numpy as np
    import seaborn as sns

    PLOTTING_AVAILABLE = True
    plt.style.use("seaborn-v0_8" if hasattr(plt.style, "seaborn-v0_8") else "default")
except ImportError:
    PLOTTING_AVAILABLE = False


class ChartGenerator:
    """Infrastructure component for generating charts"""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.color_palette = {
            "happy": "#FFD700",  # Gold
            "sad": "#87CEEB",  # Sky Blue
            "angry": "#FFB6C1",  # Light Pink (gentle)
            "scared": "#DDA0DD",  # Plum
            "curious": "#98FB98",  # Pale Green
            "calm": "#F0F8FF",  # Alice Blue
            "primary": "#4A90E2",  # Professional Blue
            "secondary": "#7ED321",  # Success Green
            "warning": "#F5A623",  # Warning Orange
            "danger": "#D0021B",  # Danger Red
        }

    def generate_charts(self, progress: ChildProgress) -> Dict[str, str]:
        """Generate all charts for the report"""
        try:
            if not PLOTTING_AVAILABLE:
                self.logger.warning(
                    "Matplotlib not available, skipping chart generation"
                )
                return {}

            charts = {}

            # 1. Emotion distribution pie chart
            charts["emotions"] = self.create_emotion_pie_chart(
                progress.emotion_analysis
            )

            # 2. Mood trends line chart
            charts["mood_trends"] = self.create_mood_trends_chart(progress.mood_trends)

            # 3. Skills practice bar chart
            charts["skills"] = self.create_skills_bar_chart(
                progress.skill_analysis.skills_practiced
            )

            # 4. Development radar chart
            charts["development"] = self.create_development_radar_chart(progress)

            return charts

        except Exception as e:
            self.logger.error(f"Chart generation error: {e}")
            return {}

    def create_emotion_pie_chart(self, emotion_analysis: EmotionDistribution) -> str:
        """Create emotion distribution pie chart"""
        try:
            if not PLOTTING_AVAILABLE or not emotion_analysis.emotions:
                return ""

            plt.figure(figsize=(8, 6))

            # Prepare data
            labels = list(emotion_analysis.emotions.keys())
            sizes = list(emotion_analysis.emotions.values())
            colors = [self.color_palette.get(emotion, "#CCCCCC") for emotion in labels]

            # Create pie chart
            plt.pie(
                sizes, labels=labels, colors=colors, autopct="%1.1f%%", startangle=90
            )
            plt.title("توزيع المشاعر خلال الفترة", fontsize=14, pad=20)
            plt.axis("equal")

            # Convert to base64
            return self._chart_to_base64()

        except Exception as e:
            self.logger.error(f"Emotion pie chart creation error: {e}")
            return ""

    def create_mood_trends_chart(self, mood_trends: Dict[str, list]) -> str:
        """Create mood trends over time"""
        try:
            if not PLOTTING_AVAILABLE or not mood_trends:
                return ""

            plt.figure(figsize=(10, 6))

            # Plot each emotion trend
            for emotion, values in mood_trends.items():
                if values:  # Only plot if there are values
                    days = list(range(len(values)))
                    color = self.color_palette.get(emotion, "#CCCCCC")
                    plt.plot(
                        days,
                        values,
                        label=emotion,
                        color=color,
                        linewidth=2,
                        marker="o",
                    )

            plt.title("اتجاهات المزاج خلال الفترة", fontsize=14)
            plt.xlabel("اليوم")
            plt.ylabel("شدة المشاعر")
            plt.legend()
            plt.grid(True, alpha=0.3)

            return self._chart_to_base64()

        except Exception as e:
            self.logger.error(f"Mood trends chart creation error: {e}")
            return ""

    def create_skills_bar_chart(self, skills: Dict[str, int]) -> str:
        """Create skills practice frequency chart"""
        try:
            if not PLOTTING_AVAILABLE or not skills:
                return ""

            plt.figure(figsize=(10, 6))

            # Sort skills by frequency
            sorted_skills = sorted(skills.items(), key=lambda x: x[1], reverse=True)
            skill_names = [skill[0] for skill in sorted_skills]
            frequencies = [skill[1] for skill in sorted_skills]

            # Create bar chart
            bars = plt.bar(
                skill_names, frequencies, color=self.color_palette["primary"], alpha=0.7
            )

            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                plt.text(
                    bar.get_x() + bar.get_width() / 2.0,
                    height,
                    f"{int(height)}",
                    ha="center",
                    va="bottom",
                )

            plt.title("المهارات المُمارسة خلال الفترة", fontsize=14)
            plt.xlabel("المهارة")
            plt.ylabel("عدد مرات الممارسة")
            plt.xticks(rotation=45, ha="right")
            plt.tight_layout()

            return self._chart_to_base64()

        except Exception as e:
            self.logger.error(f"Skills bar chart creation error: {e}")
            return ""

    def create_development_radar_chart(self, progress: ChildProgress) -> str:
        """Create developmental areas radar chart"""
        try:
            if not PLOTTING_AVAILABLE:
                return ""

            plt.figure(figsize=(8, 8))

            # Define developmental areas and their scores (0-1)
            areas = [
                "التركيز",
                "المفردات",
                "التعاطف",
                "التعاون",
                "الاستقرار العاطفي",
                "الفضول",
                "التفاعل الاجتماعي",
            ]

            scores = [
                min(progress.attention_span / 10, 1.0),  # Normalize to 0-1
                min(progress.vocabulary_growth / 20, 1.0),
                min(progress.empathy_indicators / 10, 1.0),
                progress.cooperation_level,
                progress.emotion_analysis.stability_score,
                min(progress.question_frequency / 5, 1.0),
                min(
                    (progress.sharing_behavior + progress.empathy_indicators) / 20, 1.0
                ),
            ]

            # Add first point to close the radar
            scores += scores[:1]

            # Angles for each area
            angles = np.linspace(0, 2 * np.pi, len(areas), endpoint=False).tolist()
            angles += angles[:1]

            # Create radar chart
            ax = plt.subplot(111, polar=True)
            ax.plot(
                angles, scores, "o-", linewidth=2, color=self.color_palette["primary"]
            )
            ax.fill(angles, scores, alpha=0.25, color=self.color_palette["primary"])

            # Add labels
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(areas)
            ax.set_ylim(0, 1)
            ax.set_title("مناطق التطور", size=16, pad=20)

            return self._chart_to_base64()

        except Exception as e:
            self.logger.error(f"Development radar chart creation error: {e}")
            return ""

    def _chart_to_base64(self) -> str:
        """Convert current matplotlib figure to base64 string"""
        try:
            buffer = io.BytesIO()
            plt.savefig(buffer, format="png", dpi=150, bbox_inches="tight")
            buffer.seek(0)
            chart_data = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            return chart_data

        except Exception as e:
            self.logger.error(f"Chart to base64 conversion error: {e}")
            plt.close()  # Ensure figure is closed
            return ""

    def is_available(self) -> bool:
        """Check if chart generation is available"""
        return PLOTTING_AVAILABLE
