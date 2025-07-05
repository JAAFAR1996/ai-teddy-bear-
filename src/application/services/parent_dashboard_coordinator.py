#!/usr/bin/env python3
"""
Parent Dashboard Coordinator - Single Responsibility
===================================================
مسؤول فقط عن تنسيق العمليات بين الخدمات المختلفة
"""

import logging
from datetime import datetime, timedelta
from typing import Dict

from .child_data_analyzer import ChildDataAnalyzer, DateRange
from .parent_auth_service import ParentAuthenticationService, ParentCredentials
from .parent_notification_service import (ParentNotificationService)
from .report_generator_service import (ChildProgress, ReportFormat,
                                       ReportGeneratorService)

logger = logging.getLogger(__name__)


class ParentDashboardCoordinator:
    """
    منسق لوحة الوالدين - مسؤول فقط عن تنسيق العمليات
    لا يحتوي على منطق أعمال معقد، فقط يربط بين الخدمات
    """

    def __init__(
        self,
        auth_service: ParentAuthenticationService,
        data_analyzer: ChildDataAnalyzer,
        notification_service: ParentNotificationService,
        report_generator: ReportGeneratorService,
    ):
        self.auth_service = auth_service
        self.data_analyzer = data_analyzer
        self.notification_service = notification_service
        self.report_generator = report_generator

    async def generate_weekly_report_workflow(
        self, parent_id: str, child_id: str, auth_token: str
    ) -> Dict[str, any]:
        """
        تدفق عمل إنشاء التقرير الأسبوعي - مسؤولية التنسيق فقط
        """
        try:
            # 1. التحقق من صحة المصادقة
            token_validation = await self.auth_service.validate_token(auth_token)
            if not token_validation:
                return {"success": False, "error": "Authentication failed"}

            # 2. تحليل بيانات الطفل
            week_period = DateRange(
                start_date=datetime.now() - timedelta(days=7), end_date=datetime.now()
            )

            analysis_result = await self.data_analyzer.analyze(child_id, week_period)

            # 3. تحويل نتائج التحليل إلى تقدم الطفل
            progress = self._convert_analysis_to_progress(analysis_result, child_id)

            # 4. إنشاء التقرير
            report_format = ReportFormat(format_type="html", include_charts=True)
            report_path = self.report_generator.generate_report(progress, report_format)

            # 5. إرسال إشعار للوالد
            notification_result = (
                await self.notification_service.send_weekly_report_notification(
                    parent_id=parent_id,
                    child_id=child_id,
                    report_data={
                        "child_name": progress.child_name,
                        "report_path": report_path,
                        "total_interactions": progress.total_interactions,
                    },
                )
            )

            return {
                "success": True,
                "report_path": report_path,
                "analysis": analysis_result,
                "notification_sent": notification_result.success,
            }

        except Exception as e:
            logger.error(f"Weekly report workflow error: {e}")
            return {"success": False, "error": str(e)}

    async def handle_urgent_concern_workflow(
        self, parent_id: str, child_id: str, concern_data: Dict
    ) -> Dict[str, any]:
        """
        تدفق عمل التعامل مع المخاوف العاجلة
        """
        try:
            # 1. تحليل عاجل للبيانات الحديثة
            recent_period = DateRange(
                start_date=datetime.now() - timedelta(hours=24), end_date=datetime.now()
            )

            analysis = await self.data_analyzer.analyze(child_id, recent_period)

            # 2. إرسال تنبيه عاجل
            alert_message = self._create_urgent_message(concern_data, analysis)

            notification_result = await self.notification_service.send_urgent_alert(
                parent_id=parent_id,
                child_id=child_id,
                message=alert_message,
                data=concern_data,
            )

            return {
                "success": True,
                "alert_sent": notification_result.success,
                "analysis": analysis,
            }

        except Exception as e:
            logger.error(f"Urgent concern workflow error: {e}")
            return {"success": False, "error": str(e)}

    async def authenticate_and_get_dashboard_data(
        self, email: str, password: str, child_id: str
    ) -> Dict[str, any]:
        """
        مصادقة والحصول على بيانات لوحة القيادة
        """
        try:
            # 1. المصادقة
            credentials = ParentCredentials(
                email=email, password=password, child_id=child_id
            )

            auth_result = await self.auth_service.authenticate(credentials)
            if not auth_result:
                return {"success": False, "error": "Authentication failed"}

            # 2. الحصول على التحليل الحديث
            current_week = DateRange(
                start_date=datetime.now() - timedelta(days=7), end_date=datetime.now()
            )

            analysis = await self.data_analyzer.analyze(child_id, current_week)

            return {
                "success": True,
                "auth_token": auth_result.token,
                "expires_at": auth_result.expires_at,
                "analysis": analysis,
            }

        except Exception as e:
            logger.error(f"Dashboard authentication error: {e}")
            return {"success": False, "error": str(e)}

    def _convert_analysis_to_progress(
        self, analysis_result, child_id: str
    ) -> ChildProgress:
        """تحويل نتائج التحليل إلى كائن تقدم الطفل"""
        return ChildProgress(
            child_id=child_id,
            child_name=f"Child_{child_id}",  # في التطبيق الحقيقي، نجلب الاسم من DB
            age=5,  # في التطبيق الحقيقي، نجلب العمر من DB
            period_start=analysis_result.analysis_period.start_date,
            period_end=analysis_result.analysis_period.end_date,
            total_interactions=10,  # من نتائج التحليل
            avg_daily_interactions=1.4,  # من نتائج التحليل
            dominant_emotion=analysis_result.dominant_emotion,
            attention_span=analysis_result.attention_span,
            vocabulary_growth=analysis_result.vocabulary_growth,
            skills_practiced=analysis_result.skills_progress or {},
            concerning_patterns=analysis_result.concerning_patterns,
            recommended_activities=analysis_result.development_recommendations,
        )

    def _create_urgent_message(self, concern_data: Dict, analysis) -> str:
        """إنشاء رسالة تنبيه عاجل"""
        concern_type = concern_data.get("type", "unknown")

        messages = {
            "emotion_instability": "تم رصد عدم استقرار في المشاعر لدى طفلك. يُنصح بالمتابعة",
            "short_attention_span": "انخفض مستوى التركيز لدى طفلك. قد تحتاج لاستشارة",
            "negative_emotional_dominance": "لوحظت مشاعر سلبية مهيمنة. يُرجى المتابعة الفورية",
        }

        return messages.get(concern_type, "تم رصد نمط يحتاج انتباهكم")

    async def cleanup_old_data(self, days_old: int = 30) -> Dict[str, int]:
        """تنظيف البيانات القديمة - تنسيق العملية فقط"""
        try:
            # تنظيف التقارير القديمة
            reports_cleaned = self.report_generator.cleanup_old_reports(days_old)

            logger.info(f"Cleanup completed: {reports_cleaned} reports removed")

            return {"reports_cleaned": reports_cleaned, "success": True}

        except Exception as e:
            logger.error(f"Cleanup error: {e}")
            return {"success": False, "error": str(e)}
