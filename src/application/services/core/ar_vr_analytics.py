#!/usr/bin/env python3
"""
📊 محلل بيانات AR/VR
مسؤول عن التحليلات والتقارير فقط
"""

from typing import Dict, List


class ARVRAnalytics:
    """محلل البيانات - مسؤولية واحدة فقط"""

    def calculate_learning_progress(self, sessions: List[Dict]) -> Dict:
        """حساب التقدم التعليمي"""
        all_objectives = {}

        for session in sessions:
            for objective, count in session.get(
                    "learning_progress", {}).items():
                if objective not in all_objectives:
                    all_objectives[objective] = 0
                all_objectives[objective] += count

        return {
            "mastered_objectives": [
                obj for obj, count in all_objectives.items() if count >= 5
            ],
            "learning_objectives": all_objectives,
            "total_learning_interactions": sum(all_objectives.values()),
        }

    def generate_child_report(
        self, child_id: str, sessions: List[Dict], preferences: Dict
    ) -> Dict:
        """تقرير شامل للطفل"""
        if not sessions:
            return {"message": "لا توجد جلسات مسجلة لهذا الطفل"}

        # تصنيف الجلسات
        ar_sessions = [s for s in sessions if s["type"] == "ar"]
        vr_sessions = [s for s in sessions if s["type"] == "vr"]

        # حساب الأوقات
        total_time_ar = sum(s.get("actual_duration_minutes", 0)
                            for s in ar_sessions)
        total_time_vr = sum(s.get("actual_duration_minutes", 0)
                            for s in vr_sessions)

        return {
            "summary": {
                "total_ar_sessions": len(ar_sessions),
                "total_vr_sessions": len(vr_sessions),
                "total_time_ar_minutes": total_time_ar,
                "total_time_vr_minutes": total_time_vr,
                "average_session_duration": (
                    (total_time_ar + total_time_vr) / len(sessions) if sessions else 0),
            },
            "preferences": preferences,
            "learning_progress": self.calculate_learning_progress(sessions),
            "recommendations": self.generate_personalized_recommendations(
                child_id,
                sessions,
                preferences),
        }

    def generate_personalized_recommendations(
        self, child_id: str, sessions: List[Dict], preferences: Dict
    ) -> List[str]:
        """توليد توصيات مخصصة"""
        recommendations = []

        # توصيات بناءً على التفضيلات
        if preferences.get("preferred_ar_categories"):
            top_ar_category = max(
                preferences["preferred_ar_categories"].items(),
                key=lambda x: x[1])[0]
            recommendations.append(
                f"يفضل الطفل تجارب الواقع المعزز من فئة: {top_ar_category}"
            )

        if preferences.get("preferred_vr_themes"):
            top_vr_theme = max(
                preferences["preferred_vr_themes"].items(), key=lambda x: x[1]
            )[0]
            recommendations.append(
                f"يفضل الطفل بيئات الواقع الافتراضي بموضوع: {top_vr_theme}"
            )

        # توصيات بناءً على الأداء
        recent_sessions = sessions[-5:] if len(sessions) >= 5 else sessions

        if recent_sessions:
            avg_engagement = sum(
                self._get_engagement_score(s) for s in recent_sessions
            ) / len(recent_sessions)

            if avg_engagement < 0.3:
                recommendations.append(
                    "جرب تجارب أكثر تفاعلية أو قصر مدة الجلسات")
            elif avg_engagement > 0.7:
                recommendations.append(
                    "الطفل يظهر انخراطاً عالياً - يمكن تجربة تجارب أكثر تحدياً"
                )

        # توصيات الأمان
        optimal_duration = preferences.get("optimal_session_duration", 10)
        if optimal_duration > 15:
            recommendations.append("احرص على أخذ راحات أكثر تكراراً")

        return recommendations

    def analyze_usage_patterns(self, sessions: List[Dict]) -> Dict:
        """تحليل أنماط الاستخدام"""
        if not sessions:
            return {"message": "لا توجد جلسات للتحليل"}

        # تحليل التوقيتات
        time_analysis = self._analyze_session_times(sessions)

        # تحليل التفاعل
        engagement_analysis = self._analyze_engagement_patterns(sessions)

        # تحليل التقدم
        progress_analysis = self._analyze_progress_trends(sessions)

        return {
            "time_patterns": time_analysis,
            "engagement_patterns": engagement_analysis,
            "progress_trends": progress_analysis,
            "session_count": len(sessions),
        }

    def _get_engagement_score(self, session: Dict) -> float:
        """حساب نقاط الانخراط للجلسة"""
        performance = session.get("performance_summary", {})
        engagement_level = performance.get("engagement_level", "medium")

        if engagement_level == "high":
            return 1.0
        elif engagement_level == "medium":
            return 0.5
        else:
            return 0.0

    def _analyze_session_times(self, sessions: List[Dict]) -> Dict:
        """تحليل أوقات الجلسات"""
        from datetime import datetime

        times_of_day = {"morning": 0, "afternoon": 0, "evening": 0}
        durations = []

        for session in sessions:
            try:
                start_time = datetime.fromisoformat(session["start_time"])
                hour = start_time.hour

                if 6 <= hour < 12:
                    times_of_day["morning"] += 1
                elif 12 <= hour < 18:
                    times_of_day["afternoon"] += 1
                else:
                    times_of_day["evening"] += 1

                if "actual_duration_minutes" in session:
                    durations.append(session["actual_duration_minutes"])

            except BaseException:
                continue

        avg_duration = sum(durations) / len(durations) if durations else 0

        return {
            "preferred_times": times_of_day,
            "average_duration": avg_duration,
            "duration_range": {
                "min": min(durations) if durations else 0,
                "max": max(durations) if durations else 0,
            },
        }

    def _analyze_engagement_patterns(self, sessions: List[Dict]) -> Dict:
        """تحليل أنماط الانخراط"""
        engagement_scores = []
        interaction_counts = []

        for session in sessions:
            engagement_scores.append(self._get_engagement_score(session))
            interaction_counts.append(len(session.get("interaction_log", [])))

        avg_engagement = (sum(engagement_scores) /
                          len(engagement_scores) if engagement_scores else 0)
        avg_interactions = (
            sum(interaction_counts) / len(interaction_counts)
            if interaction_counts
            else 0
        )

        return {
            "average_engagement": avg_engagement,
            "average_interactions_per_session": avg_interactions,
            "engagement_trend": self._calculate_trend(engagement_scores),
        }

    def _analyze_progress_trends(self, sessions: List[Dict]) -> Dict:
        """تحليل اتجاهات التقدم"""
        progress_over_time = []

        for session in sessions:
            session_progress = sum(
                session.get(
                    "learning_progress",
                    {}).values())
            progress_over_time.append(session_progress)

        return {
            "total_progress": sum(progress_over_time),
            "progress_per_session": progress_over_time,
            "progress_trend": self._calculate_trend(progress_over_time),
        }

    def _calculate_trend(self, values: List[float]) -> str:
        """حساب الاتجاه (صاعد/ثابت/هابط)"""
        if len(values) < 2:
            return "insufficient_data"

        # مقارنة النصف الأول بالثاني
        mid = len(values) // 2
        first_half_avg = sum(values[:mid]) / mid if mid > 0 else 0
        second_half_avg = (
            sum(values[mid:]) / (len(values) - mid) if (len(values) - mid) > 0 else 0
        )

        if second_half_avg > first_half_avg * 1.1:
            return "improving"
        elif second_half_avg < first_half_avg * 0.9:
            return "declining"
        else:
            return "stable"

    def generate_session_recommendations(self, session: Dict) -> List[str]:
        """توصيات لجلسة محددة"""
        recommendations = []
        performance = session.get("performance_summary", {})

        if performance.get("engagement_level") == "low":
            recommendations.append("جرب تجربة أكثر تفاعلية في المرة القادمة")

        if performance.get("comfort_level") == "low":
            recommendations.append("خذ راحات أكثر تكراراً")
            recommendations.append("قلل من مدة الجلسة")

        if performance.get("technical_issues", 0) > 2:
            recommendations.append("تحقق من جودة الاتصال والإضاءة")

        if session.get("actual_duration_minutes", 0) > 15:
            recommendations.append("حاول تقليل مدة الجلسة للحفاظ على الراحة")

        return recommendations

    def compare_children_performance(
        self, children_data: Dict[str, List[Dict]]
    ) -> Dict:
        """مقارنة أداء الأطفال (مجهول الهوية)"""
        if len(children_data) < 2:
            return {"message": "يحتاج بيانات طفلين على الأقل للمقارنة"}

        aggregated_stats = {}

        for child_id, sessions in children_data.items():
            child_stats = self.analyze_usage_patterns(sessions)
            aggregated_stats[f"child_{len(aggregated_stats) + 1}"] = {
                "session_count": len(sessions), "avg_engagement": child_stats.get(
                    "engagement_patterns", {}).get(
                    "average_engagement", 0), "total_progress": child_stats.get(
                    "progress_trends", {}).get(
                    "total_progress", 0), }

        return {
            "comparison": aggregated_stats,
            "insights": self._generate_comparison_insights(aggregated_stats),
        }

    def _generate_comparison_insights(self, stats: Dict) -> List[str]:
        """توليد رؤى من المقارنة"""
        insights = []

        # العثور على أفضل انخراط
        best_engagement = max(
            stats.values(),
            key=lambda x: x["avg_engagement"])
        worst_engagement = min(
            stats.values(),
            key=lambda x: x["avg_engagement"])

        if best_engagement["avg_engagement"] > worst_engagement["avg_engagement"] * 1.5:
            insights.append("هناك تفاوت كبير في مستويات الانخراط بين الأطفال")

        # متوسط عدد الجلسات
        avg_sessions = sum(child["session_count"]
                           for child in stats.values()) / len(stats)
        insights.append(f"متوسط عدد الجلسات: {avg_sessions:.1f}")

        return insights
