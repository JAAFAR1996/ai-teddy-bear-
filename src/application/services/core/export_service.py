"""
Export Service
=============

Infrastructure service for exporting data in various formats (PDF, Excel, JSON).
"""

import json
import logging
from datetime import datetime
from io import BytesIO
from typing import Any, Dict, List

import pandas as pd

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )

    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


class ExportService:
    """Service for exporting conversation and analytics data"""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        if not REPORTLAB_AVAILABLE:
            self.logger.warning(
                "ReportLab not available - PDF export will be limited")

    async def export_conversation_history_as_json(
        self, conversations: List[Dict[str, Any]]
    ) -> bytes:
        """Export conversation history as JSON"""

        try:
            export_data = {
                "exported_at": datetime.now().isoformat(),
                "total_conversations": len(conversations),
                "conversations": conversations,
            }

            return json.dumps(
                export_data,
                indent=2,
                ensure_ascii=False).encode("utf-8")

        except Exception as e:
            self.logger.error(f"Error exporting as JSON: {e}")
            return b'{"error": "Export failed"}'

    async def export_conversation_history_as_excel(
        self, conversations: List[Dict[str, Any]]
    ) -> bytes:
        """Export conversation history as Excel file"""

        try:
            # Prepare data for Excel
            excel_data = []

            for conv in conversations:
                excel_data.append(
                    {
                        "Date": conv.get(
                            "started_at", ""), "Duration (minutes)": conv.get(
                            "duration_seconds", 0) / 60, "Messages": conv.get(
                            "message_count", 0), "Topics": ", ".join(
                            conv.get(
                                "topics", [])), "Sentiment": conv.get(
                                "sentiment_scores", {}).get(
                                    "positive", 0), "Quality Score": conv.get(
                                        "quality_score", 0), "Summary": conv.get(
                                            "summary", ""), })

            # Create DataFrame
            df = pd.DataFrame(excel_data)

            # Write to Excel
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
                df.to_excel(
                    writer,
                    sheet_name="Conversation History",
                    index=False)

                # Get workbook and worksheet for formatting
                workbook = writer.book
                worksheet = writer.sheets["Conversation History"]

                # Add formatting
                header_format = workbook.add_format(
                    {
                        "bold": True,
                        "text_wrap": True,
                        "valign": "top",
                        "fg_color": "#D7E4BC",
                        "border": 1,
                    }
                )

                # Write headers with formatting
                for col_num, value in enumerate(df.columns.values):
                    worksheet.write(0, col_num, value, header_format)

                # Auto-adjust column widths
                for i, col in enumerate(df.columns):
                    max_length = max(
                        df[col].astype(str).map(len).max(), len(col))
                    worksheet.set_column(i, i, min(max_length + 2, 50))

            buffer.seek(0)
            return buffer.read()

        except Exception as e:
            self.logger.error(f"Error exporting as Excel: {e}")
            return b""

    def _create_pdf_summary_table(self, conversations: List[Dict[str, Any]]) -> "Table":
        """Creates the summary table for the PDF report."""
        summary_data = [
            ["Total Conversations", str(len(conversations))],
            ["Export Date", datetime.now().strftime("%Y-%m-%d %H:%M")],
        ]
        if conversations:
            total_duration = (sum(c.get("duration_seconds", 0)
                                  for c in conversations) / 60)
            avg_duration = (
                total_duration / len(conversations) if conversations else 0
            )
            summary_data.extend(
                [
                    ["Total Duration (minutes)", f"{total_duration:.1f}"],
                    ["Average Session (minutes)", f"{avg_duration:.1f}"],
                ]
            )
        summary_table = Table(summary_data)
        summary_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 12),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )
        return summary_table

    def _create_pdf_conversations_table(self, conversations: List[Dict[str, Any]]) -> "Table":
        """Creates the detailed conversations table for the PDF report."""
        table_data = [
            ["Date", "Duration (min)", "Messages", "Topics", "Summary"]
        ]
        for conv in conversations[:20]:  # Limit to 20 for PDF size
            row = [
                conv.get("started_at", "")[:10],  # Date only
                f"{conv.get('duration_seconds', 0) / 60:.1f}",
                str(conv.get("message_count", 0)),
                ", ".join(conv.get("topics", [])[:3]),  # Limit topics
                (
                    conv.get("summary", "")[:100] + "..."
                    if len(conv.get("summary", "")) > 100
                    else conv.get("summary", "")
                ),
            ]
            table_data.append(row)
        conv_table = Table(
            table_data,
            colWidths=[
                1.2 * inch,
                1 * inch,
                0.8 * inch,
                1.5 * inch,
                2.5 * inch,
            ],
        )
        conv_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 10),
                    ("FONTSIZE", (0, 1), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )
        return conv_table

    async def export_conversation_history_as_pdf(
        self, conversations: List[Dict[str, Any]], child_name: str = "Child"
    ) -> bytes:
        """Export conversation history as PDF"""

        try:
            if not REPORTLAB_AVAILABLE:
                return self._export_simple_text_pdf(conversations, child_name)

            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []

            # Title
            title_style = ParagraphStyle(
                "CustomTitle",
                parent=styles["Heading1"],
                fontSize=18,
                spaceAfter=30,
                textColor=colors.darkblue,
            )

            story.append(
                Paragraph(
                    f"Conversation History - {child_name}",
                    title_style))
            story.append(Spacer(1, 20))

            # Summary section
            story.append(Paragraph("Summary", styles["Heading2"]))
            summary_table = self._create_pdf_summary_table(conversations)
            story.append(summary_table)
            story.append(Spacer(1, 20))

            # Conversations table
            if conversations:
                story.append(
                    Paragraph(
                        "Detailed Conversations",
                        styles["Heading2"]))
                conv_table = self._create_pdf_conversations_table(
                    conversations)
                story.append(conv_table)

            # Build PDF
            doc.build(story)
            buffer.seek(0)
            return buffer.read()

        except Exception as e:
            self.logger.error(f"Error exporting as PDF: {e}")
            return self._export_simple_text_pdf(conversations, child_name)

    def _export_simple_text_pdf(
        self, conversations: List[Dict[str, Any]], child_name: str
    ) -> bytes:
        """Fallback simple text-based PDF export"""

        try:
            content = f"Conversation History - {child_name}\n"
            content += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
            content += "=" * 50 + "\n\n"

            content += f"Total Conversations: {len(conversations)}\n\n"

            for i, conv in enumerate(conversations[:10], 1):
                content += f"Conversation {i}:\n"
                content += f"  Date: {conv.get('started_at', 'Unknown')}\n"
                content += (
                    f"  Duration: {conv.get('duration_seconds', 0) / 60:.1f} minutes\n"
                )
                content += f"  Messages: {conv.get('message_count', 0)}\n"
                content += f"  Topics: {', '.join(conv.get('topics', []))}\n"
                content += f"  Summary: {conv.get('summary', 'No summary')}\n"
                content += "-" * 30 + "\n\n"

            return content.encode("utf-8")

        except Exception as e:
            self.logger.error(f"Error in fallback PDF export: {e}")
            return b"Export failed"

    async def export_analytics_report(
        self, analytics_data: Dict[str, Any], child_name: str, format_type: str = "pdf"
    ) -> bytes:
        """Export analytics report in specified format"""

        try:
            if format_type.lower() == "json":
                export_data = {
                    "child_name": child_name,
                    "generated_at": datetime.now().isoformat(),
                    "analytics": analytics_data,
                }
                return json.dumps(
                    export_data,
                    indent=2,
                    ensure_ascii=False).encode("utf-8")

            elif format_type.lower() == "excel":
                return await self._export_analytics_excel(analytics_data, child_name)

            else:  # PDF
                return await self._export_analytics_pdf(analytics_data, child_name)

        except Exception as e:
            self.logger.error(f"Error exporting analytics report: {e}")
            return b"Export failed"

    async def _export_analytics_excel(
        self, analytics_data: Dict[str, Any], child_name: str
    ) -> bytes:
        """Export analytics as Excel"""

        buffer = BytesIO()

        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            # Summary sheet
            summary_data = {
                "Metric": [
                    "Total Conversations",
                    "Total Duration (minutes)",
                    "Average Session (minutes)",
                    "Quality Score",
                ],
                "Value": [
                    analytics_data.get("total_conversations", 0),
                    analytics_data.get("total_duration_minutes", 0),
                    analytics_data.get("average_session_minutes", 0),
                    analytics_data.get("interaction_quality_score", 0),
                ],
            }

            pd.DataFrame(summary_data).to_excel(
                writer, sheet_name="Summary", index=False
            )

            # Topics sheet
            if "topics_frequency" in analytics_data:
                topics_data = pd.DataFrame(
                    list(analytics_data["topics_frequency"].items()),
                    columns=["Topic", "Frequency"],
                )
                topics_data.to_excel(writer, sheet_name="Topics", index=False)

        buffer.seek(0)
        return buffer.read()

    async def _export_analytics_pdf(
        self, analytics_data: Dict[str, Any], child_name: str
    ) -> bytes:
        """Export analytics as PDF"""

        if not REPORTLAB_AVAILABLE:
            # Simple text export
            content = f"Analytics Report - {child_name}\n"
            content += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
            content += "=" * 50 + "\n\n"

            content += (
                f"Total Conversations: {analytics_data.get('total_conversations', 0)}\n"
            )
            content += f"Total Duration: {analytics_data.get('total_duration_minutes', 0):.1f} minutes\n"
            content += f"Average Session: {analytics_data.get('average_session_minutes', 0):.1f} minutes\n"
            content += f"Quality Score: {analytics_data.get('interaction_quality_score', 0):.2f}\n"

            return content.encode("utf-8")

        # Full PDF with ReportLab
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        # Title
        story.append(
            Paragraph(
                f"Analytics Report - {child_name}",
                styles["Title"]))
        story.append(Spacer(1, 20))

        # Metrics table
        metrics_data = [
            ["Metric", "Value"],
            ["Total Conversations", str(
                analytics_data.get("total_conversations", 0))],
            [
                "Total Duration (minutes)",
                f"{analytics_data.get('total_duration_minutes', 0):.1f}",
            ],
            [
                "Average Session (minutes)",
                f"{analytics_data.get('average_session_minutes', 0):.1f}",
            ],
            [
                "Quality Score",
                f"{analytics_data.get('interaction_quality_score', 0):.2f}",
            ],
        ]

        metrics_table = Table(metrics_data)
        metrics_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 12),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )

        story.append(metrics_table)

        doc.build(story)
        buffer.seek(0)
        return buffer.read()
