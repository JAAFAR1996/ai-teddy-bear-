#!/usr/bin/env python3
"""
Report Generator Service - Single Responsibility
===============================================
مسؤول فقط عن إنشاء التقارير بأشكال مختلفة
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class ChildProgress:
    """بيانات تقدم الطفل"""

    child_id: str
    child_name: str
    age: int
    period_start: datetime
    period_end: datetime
    total_interactions: int
    avg_daily_interactions: float
    dominant_emotion: str
    attention_span: float
    vocabulary_growth: int
    skills_practiced: Dict[str, int]
    concerning_patterns: list
    recommended_activities: list


@dataclass
class ReportFormat:
    """تنسيق التقرير"""

    format_type: str  # 'json', 'html', 'text', 'pdf'
    template_name: Optional[str] = None
    include_charts: bool = False
    language: str = "ar"


class ReportGeneratorService:
    """مسؤول فقط عن إنشاء التقارير"""

    def __init__(self, template_service=None):
        self.template_service = template_service
        self.output_directory = Path("reports")
        self.output_directory.mkdir(exist_ok=True)

    def generate_report(self, progress: ChildProgress, format: ReportFormat) -> str:
        """
        إنشاء تقرير - المسؤولية الوحيدة لهذا الكلاس

        Args:
            progress: بيانات تقدم الطفل
            format: تنسيق التقرير المطلوب

        Returns:
            path to generated report file
        """
        try:
            # اختيار نوع التقرير
            if format.format_type == "json":
                return self._generate_json_report(progress)
            elif format.format_type == "html":
                return self._generate_html_report(progress, format)
            elif format.format_type == "text":
                return self._generate_text_report(progress)
            elif format.format_type == "pdf":
                return self._generate_pdf_report(progress, format)
            else:
                raise ValueError(f"Unsupported format: {format.format_type}")

        except Exception as e:
            logger.error(f"Report generation error: {e}")
            return ""

    def _generate_json_report(self, progress: ChildProgress) -> str:
        """إنشاء تقرير JSON"""
        try:
            report_data = {
                "child_info": {
                    "id": progress.child_id,
                    "name": progress.child_name,
                    "age": progress.age,
                },
                "period": {
                    "start": progress.period_start.isoformat(),
                    "end": progress.period_end.isoformat(),
                },
                "metrics": {
                    "total_interactions": progress.total_interactions,
                    "avg_daily_interactions": progress.avg_daily_interactions,
                    "dominant_emotion": progress.dominant_emotion,
                    "attention_span": progress.attention_span,
                    "vocabulary_growth": progress.vocabulary_growth,
                },
                "skills_practiced": progress.skills_practiced,
                "analysis": {
                    "concerning_patterns": progress.concerning_patterns,
                    "recommended_activities": progress.recommended_activities,
                },
                "generated_at": datetime.now().isoformat(),
            }

            filename = (
                f"report_{progress.child_id}_{datetime.now().strftime('%Y%m%d')}.json"
            )
            filepath = self.output_directory / filename

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)

            logger.info(f"JSON report generated: {filepath}")
            return str(filepath)

        except Exception as e:
            logger.error(f"JSON report generation error: {e}")
            return ""

    def _generate_html_report(
        self, progress: ChildProgress, format: ReportFormat
    ) -> str:
        """إنشاء تقرير HTML"""
        try:
            html_content = self._create_html_template(progress, format)

            filename = (
                f"report_{progress.child_id}_{datetime.now().strftime('%Y%m%d')}.html"
            )
            filepath = self.output_directory / filename

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html_content)

            logger.info(f"HTML report generated: {filepath}")
            return str(filepath)

        except Exception as e:
            logger.error(f"HTML report generation error: {e}")
            return ""

    def _generate_text_report(self, progress: ChildProgress) -> str:
        """إنشاء تقرير نصي"""
        try:
            text_content = f"""
🧸 تقرير تقدم الطفل - {progress.child_name}
========================================

📅 الفترة: {progress.period_start.strftime('%Y-%m-%d')} إلى {progress.period_end.strftime('%Y-%m-%d')}
👶 العمر: {progress.age} سنوات

📊 ملخص التفاعلات:
- إجمالي التفاعلات: {progress.total_interactions}
- متوسط التفاعلات اليومية: {progress.avg_daily_interactions:.1f}
- المشاعر المهيمنة: {progress.dominant_emotion}
- مدة التركيز: {progress.attention_span:.1f} دقيقة
- نمو المفردات: {progress.vocabulary_growth} كلمة جديدة

🎯 المهارات المُمارسة:
"""

            for skill, count in progress.skills_practiced.items():
                text_content += f"- {skill}: {count} مرة\n"

            if progress.concerning_patterns:
                text_content += "\n⚠️ نقاط تحتاج انتباه:\n"
                for concern in progress.concerning_patterns:
                    text_content += f"- {concern}\n"

            if progress.recommended_activities:
                text_content += "\n💡 الأنشطة المُوصى بها:\n"
                for activity in progress.recommended_activities:
                    text_content += f"- {activity}\n"

            text_content += (
                f"\n📋 تم إنشاء التقرير في: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            )

            filename = (
                f"report_{progress.child_id}_{datetime.now().strftime('%Y%m%d')}.txt"
            )
            filepath = self.output_directory / filename

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(text_content)

            logger.info(f"Text report generated: {filepath}")
            return str(filepath)

        except Exception as e:
            logger.error(f"Text report generation error: {e}")
            return ""

    def _generate_pdf_report(
        self, progress: ChildProgress, format: ReportFormat
    ) -> str:
        """إنشاء تقرير PDF"""
        try:
            # في التطبيق الحقيقي، نستخدم مكتبة PDF مثل reportlab
            logger.info("PDF generation requires additional libraries")

            # للآن، ننشئ تقرير نصي كبديل
            return self._generate_text_report(progress)

        except Exception as e:
            logger.error(f"PDF report generation error: {e}")
            return ""

    def _create_html_template(
        self, progress: ChildProgress, format: ReportFormat
    ) -> str:
        """إنشاء قالب HTML"""
        template = f"""
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تقرير تقدم {progress.child_name}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            direction: rtl;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .metric {{
            background: #f8f9fa;
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid #007bff;
            border-radius: 5px;
        }}
        .skills-list {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
            margin: 20px 0;
        }}
        .skill-item {{
            background: #e3f2fd;
            padding: 10px;
            border-radius: 5px;
            text-align: center;
        }}
        .concerns {{
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .recommendations {{
            background: #d1ecf1;
            border: 1px solid #bee5eb;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧸 تقرير تقدم الطفل</h1>
            <h2>{progress.child_name}</h2>
            <p>العمر: {progress.age} سنوات | الفترة: {progress.period_start.strftime('%Y-%m-%d')} - {progress.period_end.strftime('%Y-%m-%d')}</p>
        </div>
        
        <div class="metric">
            <strong>📊 إجمالي التفاعلات:</strong> {progress.total_interactions}
        </div>
        
        <div class="metric">
            <strong>📈 متوسط التفاعلات اليومية:</strong> {progress.avg_daily_interactions:.1f}
        </div>
        
        <div class="metric">
            <strong>😊 المشاعر المهيمنة:</strong> {progress.dominant_emotion}
        </div>
        
        <div class="metric">
            <strong>⏱️ مدة التركيز:</strong> {progress.attention_span:.1f} دقيقة
        </div>
        
        <div class="metric">
            <strong>📚 نمو المفردات:</strong> {progress.vocabulary_growth} كلمة جديدة
        </div>
        
        <h3>🎯 المهارات المُمارسة</h3>
        <div class="skills-list">
        """

        for skill, count in progress.skills_practiced.items():
            template += f"""
            <div class="skill-item">
                <strong>{skill}</strong><br>
                {count} مرة
            </div>
            """

        template += "</div>"

        if progress.concerning_patterns:
            template += """
            <div class="concerns">
                <h3>⚠️ نقاط تحتاج انتباه</h3>
                <ul>
            """
            for concern in progress.concerning_patterns:
                template += f"<li>{concern}</li>"
            template += "</ul></div>"

        if progress.recommended_activities:
            template += """
            <div class="recommendations">
                <h3>💡 الأنشطة المُوصى بها</h3>
                <ul>
            """
            for activity in progress.recommended_activities:
                template += f"<li>{activity}</li>"
            template += "</ul></div>"

        template += f"""
        <div style="text-align: center; margin-top: 30px; color: #666;">
            <p>تم إنشاء التقرير في: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        </div>
    </div>
</body>
</html>
        """

        return template

    def get_available_formats(self) -> list:
        """الحصول على التنسيقات المتاحة"""
        return ["json", "html", "text", "pdf"]

    def cleanup_old_reports(self, days_old: int = 30) -> int:
        """تنظيف التقارير القديمة"""
        try:
            deleted_count = 0
            cutoff_date = datetime.now().timestamp() - (days_old * 24 * 60 * 60)

            for file_path in self.output_directory.glob("report_*"):
                if file_path.stat().st_mtime < cutoff_date:
                    file_path.unlink()
                    deleted_count += 1

            logger.info(f"Cleaned up {deleted_count} old reports")
            return deleted_count

        except Exception as e:
            logger.error(f"Cleanup error: {e}")
            return 0
