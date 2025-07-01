"""
PDF Generation Infrastructure
Handles PDF report creation using ReportLab
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from src.domain.reporting.models import ChildProgress

# Optional imports for PDF generation
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.pdfgen import canvas
    from reportlab.platypus import (Paragraph, SimpleDocTemplate, Spacer,
                                    Table, TableStyle)

    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


class PDFGenerator:
    """Infrastructure component for generating PDF reports"""

    def __init__(self, output_directory: str = "reports"):
        self.output_dir = Path(output_directory)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(self.__class__.__name__)

    def create_pdf_report(self, progress: ChildProgress, charts: Dict[str, str]) -> str:
        """Create comprehensive PDF report"""
        try:
            if not PDF_AVAILABLE:
                return self.create_text_report(progress)

            # Create PDF file path
            filename = f"تقرير_{progress.child_name}_{progress.period.end_date.strftime('%Y-%m-%d')}.pdf"
            filepath = self.output_dir / filename

            # Create PDF document
            doc = SimpleDocTemplate(str(filepath), pagesize=A4)

            # Build story (content)
            story = self._build_pdf_content(progress, charts)

            # Build PDF
            doc.build(story)

            self.logger.info(f"Created PDF report: {filepath}")
            return str(filepath)

        except Exception as e:
            self.logger.error(f"PDF creation error: {e}")
            return self.create_text_report(progress)

    def _build_pdf_content(
        self, progress: ChildProgress, charts: Dict[str, str]
    ) -> list:
        """Build PDF content structure"""
        try:
            story = []
            styles = getSampleStyleSheet()

            # Title
            title = Paragraph(
                f"تقرير تقدم الطفل - {progress.child_name}", styles["Title"]
            )
            story.append(title)
            story.append(Spacer(1, 12))

            # Period info
            period_text = (
                f"الفترة: {progress.period.start_date.strftime('%Y-%m-%d')} "
                f"إلى {progress.period.end_date.strftime('%Y-%m-%d')}"
            )
            story.append(Paragraph(period_text, styles["Normal"]))
            story.append(Spacer(1, 12))

            # Summary statistics table
            story.append(self._create_summary_table(progress, styles))
            story.append(Spacer(1, 20))

            # Emotional analysis section
            story.append(Paragraph("التحليل العاطفي", styles["Heading2"]))
            emotion_text = (
                f"المشاعر المهيمنة: {progress.emotion_analysis.dominant_emotion}<br/>"
                f"استقرار المشاعر: {progress.emotion_analysis.stability_score:.1%}"
            )
            story.append(Paragraph(emotion_text, styles["Normal"]))
            story.append(Spacer(1, 12))

            # Skills analysis section
            story.append(Paragraph("تحليل المهارات", styles["Heading2"]))
            skills_text = (
                f"إجمالي جلسات الممارسة: {progress.skill_analysis.get_total_practice_sessions()}<br/>"
                f"مهارات جديدة: {len(progress.skill_analysis.new_skills_learned)}"
            )
            story.append(Paragraph(skills_text, styles["Normal"]))
            story.append(Spacer(1, 12))

            # Achievements section
            if progress.learning_achievements:
                story.append(Paragraph("الإنجازات", styles["Heading2"]))
                for achievement in progress.learning_achievements[:5]:
                    story.append(Paragraph(f"• {achievement}", styles["Normal"]))
                story.append(Spacer(1, 12))

            # Recommendations section
            if progress.recommended_activities:
                story.append(Paragraph("التوصيات", styles["Heading2"]))
                for recommendation in progress.recommended_activities[:5]:
                    story.append(Paragraph(f"• {recommendation}", styles["Normal"]))
                story.append(Spacer(1, 12))

            # Concerns section (if any)
            if progress.concerning_patterns:
                story.append(Paragraph("نقاط تحتاج انتباه", styles["Heading2"]))
                for concern in progress.concerning_patterns:
                    story.append(Paragraph(f"⚠️ {concern}", styles["Normal"]))
                story.append(Spacer(1, 12))

            # Charts placeholders (in real implementation, embed actual charts)
            for chart_name in charts.keys():
                story.append(
                    Paragraph(f"الرسم البياني: {chart_name}", styles["Heading3"])
                )
                story.append(Spacer(1, 100))  # Placeholder space for chart

            return story

        except Exception as e:
            self.logger.error(f"PDF content building error: {e}")
            return []

    def _create_summary_table(self, progress: ChildProgress, styles) -> Table:
        """Create summary statistics table"""
        try:
            summary_data = [
                ["المقياس", "القيمة"],
                ["إجمالي التفاعلات", str(progress.total_interactions)],
                ["متوسط التفاعلات اليومية", f"{progress.avg_daily_interactions:.1f}"],
                ["المشاعر المهيمنة", progress.emotion_analysis.dominant_emotion],
                ["مدة التركيز (دقائق)", f"{progress.attention_span:.1f}"],
                ["نمو المفردات", str(progress.vocabulary_growth)],
                ["مؤشرات التعاطف", str(progress.empathy_indicators)],
                ["مستوى التعاون", f"{progress.cooperation_level:.1%}"],
            ]

            table = Table(summary_data)
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 12),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ]
                )
            )

            return table

        except Exception as e:
            self.logger.error(f"Summary table creation error: {e}")
            return Table([["خطأ في إنشاء الجدول"]])

    def create_text_report(self, progress: ChildProgress) -> str:
        """Create simple text-based report when PDF is not available"""
        try:
            report_content = f"""
🧸 تقرير تقدم الطفل - {progress.child_name}
========================================

📅 الفترة: {progress.period.start_date.strftime('%Y-%m-%d')} إلى {progress.period.end_date.strftime('%Y-%m-%d')}
👶 العمر: {progress.age} سنوات

📊 ملخص التفاعلات:
- إجمالي التفاعلات: {progress.total_interactions}
- متوسط التفاعلات اليومية: {progress.avg_daily_interactions:.1f}
- أطول محادثة: {progress.longest_conversation} دقيقة

😊 التحليل العاطفي:
- المشاعر المهيمنة: {progress.emotion_analysis.dominant_emotion}
- استقرار المشاعر: {progress.emotion_analysis.stability_score:.1%}
- مؤشرات التعاطف: {progress.empathy_indicators}

🎯 تحليل المهارات:
- إجمالي جلسات الممارسة: {progress.skill_analysis.get_total_practice_sessions()}
- مهارات جديدة تم تعلمها: {len(progress.skill_analysis.new_skills_learned)}
- مدة التركيز المتوسطة: {progress.attention_span:.1f} دقيقة

🏆 الإنجازات:
"""

            for achievement in progress.learning_achievements[:5]:
                report_content += f"- {achievement}\n"

            report_content += "\n💡 التوصيات:\n"
            for recommendation in progress.recommended_activities[:5]:
                report_content += f"- {recommendation}\n"

            if progress.concerning_patterns:
                report_content += "\n⚠️ نقاط تحتاج انتباه:\n"
                for concern in progress.concerning_patterns:
                    report_content += f"- {concern}\n"

            report_content += f"\n📝 تم إنشاء التقرير في: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

            # Save text report
            filename = f"تقرير_نصي_{progress.child_name}_{progress.period.end_date.strftime('%Y-%m-%d')}.txt"
            filepath = self.output_dir / filename

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(report_content)

            self.logger.info(f"Created text report: {filepath}")
            return str(filepath)

        except Exception as e:
            self.logger.error(f"Text report creation error: {e}")
            return ""

    def is_available(self) -> bool:
        """Check if PDF generation is available"""
        return PDF_AVAILABLE
