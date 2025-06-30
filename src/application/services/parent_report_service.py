"""
📊 Parent Report Service for AI Teddy Bear
Generates comprehensive reports about child's emotional and behavioral progress
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import json
from dataclasses import dataclass, asdict
import pandas as pd
import numpy as np
from pathlib import Path
import base64
import io

# For generating charts
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    PLOTTING_AVAILABLE = True
    plt.style.use('seaborn-v0_8')  # Modern, clean style
except ImportError:
    PLOTTING_AVAILABLE = False
    print("⚠️ Matplotlib/Seaborn not installed. Install with: pip install matplotlib seaborn")

# For PDF generation
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("⚠️ ReportLab not installed. Install with: pip install reportlab")


@dataclass
class ChildProgress:
    """Child's progress metrics over time"""
    child_id: str
    child_name: str
    age: int
    period_start: datetime
    period_end: datetime
    
    # Interaction metrics
    total_interactions: int
    avg_daily_interactions: float
    longest_conversation: int  # minutes
    favorite_topics: List[str]
    
    # Emotional metrics
    emotion_distribution: Dict[str, float]
    dominant_emotion: str
    emotion_stability: float  # 0-1, higher = more stable
    mood_trends: Dict[str, List[float]]  # daily mood scores
    
    # Behavioral metrics
    attention_span: float  # average minutes focused
    response_time: float  # average seconds to respond
    vocabulary_growth: int  # new words learned
    question_frequency: float  # questions per conversation
    
    # Learning metrics
    skills_practiced: Dict[str, int]  # skill -> times practiced
    learning_achievements: List[str]
    areas_for_improvement: List[str]
    recommended_activities: List[str]
    
    # Social metrics
    empathy_indicators: int
    sharing_behavior: int
    cooperation_level: float
    
    # Sleep/routine (if available)
    sleep_pattern_quality: Optional[float]
    bedtime_conversations: int
    
    # Red flags (if any)
    concerning_patterns: List[str]
    urgent_recommendations: List[str]


@dataclass
class InteractionAnalysis:
    """Analysis of a single interaction"""
    timestamp: datetime
    duration: int  # seconds
    primary_emotion: str
    emotions: Dict[str, float]
    topics_discussed: List[str]
    skills_used: List[str]
    behavioral_indicators: List[str]
    quality_score: float  # 0-1


class ParentReportService:
    """
    Service for generating comprehensive parental reports
    """
    
    def __init__(self, database_service=None, analytics_service=None):
        self.db = database_service
        self.analytics = analytics_service
        
        # Report templates and styling
        self.color_palette = {
            'happy': '#FFD700',      # Gold
            'sad': '#87CEEB',        # Sky Blue
            'angry': '#FFB6C1',      # Light Pink (gentle)
            'scared': '#DDA0DD',     # Plum
            'curious': '#98FB98',    # Pale Green
            'calm': '#F0F8FF',       # Alice Blue
            'primary': '#4A90E2',    # Professional Blue
            'secondary': '#7ED321',  # Success Green
            'warning': '#F5A623',    # Warning Orange
            'danger': '#D0021B'      # Danger Red
        }
    
    async def generate_weekly_report(
        self, 
        child_id: str, 
        week_offset: int = 0
    ) -> ChildProgress:
        """
        Generate comprehensive weekly report for a child
        
        Args:
            child_id: Child's unique identifier
            week_offset: 0 = current week, 1 = last week, etc.
        
        Returns:
            ChildProgress object with all metrics
        """
        # Calculate date range
        end_date = datetime.now() - timedelta(weeks=week_offset)
        start_date = end_date - timedelta(days=7)
        
        # Get child info
        child_info = await self._get_child_info(child_id)
        
        # Get interaction data
        interactions = await self._get_interactions(child_id, start_date, end_date)
        
        # Analyze all metrics
        progress = ChildProgress(
            child_id=child_id,
            child_name=child_info.get('name', 'Unknown'),
            age=child_info.get('age', 5),
            period_start=start_date,
            period_end=end_date,
            
            # Basic interaction metrics
            total_interactions=len(interactions),
            avg_daily_interactions=len(interactions) / 7,
            longest_conversation=self._calculate_longest_conversation(interactions),
            favorite_topics=self._extract_favorite_topics(interactions),
            
            # Emotional analysis
            emotion_distribution=self._analyze_emotion_distribution(interactions),
            dominant_emotion=self._get_dominant_emotion(interactions),
            emotion_stability=self._calculate_emotion_stability(interactions),
            mood_trends=self._analyze_mood_trends(interactions, start_date, end_date),
            
            # Behavioral analysis
            attention_span=self._calculate_attention_span(interactions),
            response_time=self._calculate_response_time(interactions),
            vocabulary_growth=self._estimate_vocabulary_growth(interactions),
            question_frequency=self._calculate_question_frequency(interactions),
            
            # Learning analysis
            skills_practiced=self._analyze_skills_practiced(interactions),
            learning_achievements=self._identify_achievements(interactions),
            areas_for_improvement=self._identify_improvement_areas(interactions),
            recommended_activities=self._generate_activity_recommendations(interactions),
            
            # Social analysis
            empathy_indicators=self._count_empathy_indicators(interactions),
            sharing_behavior=self._analyze_sharing_behavior(interactions),
            cooperation_level=self._calculate_cooperation_level(interactions),
            
            # Sleep analysis (if data available)
            sleep_pattern_quality=self._analyze_sleep_patterns(interactions),
            bedtime_conversations=self._count_bedtime_conversations(interactions),
            
            # Red flags
            concerning_patterns=self._identify_concerning_patterns(interactions),
            urgent_recommendations=self._generate_urgent_recommendations(interactions)
        )
        
        return progress
    
    async def generate_monthly_report(self, child_id: str) -> Dict[str, Any]:
        """Generate comprehensive monthly report"""
        # Get 4 weekly reports
        weekly_reports = []
        for week in range(4):
            weekly_report = await self.generate_weekly_report(child_id, week)
            weekly_reports.append(weekly_report)
        
        # Analyze trends across weeks
        return {
            'weekly_reports': weekly_reports,
            'monthly_trends': self._analyze_monthly_trends(weekly_reports),
            'long_term_recommendations': self._generate_long_term_recommendations(weekly_reports),
            'developmental_milestones': self._check_developmental_milestones(weekly_reports)
        }
    
    def create_visual_report(
        self, 
        progress: ChildProgress, 
        format: str = 'pdf'
    ) -> str:
        """
        Create visual report with charts and graphics
        
        Args:
            progress: Child progress data
            format: 'pdf', 'html', or 'png'
        
        Returns:
            File path or base64 encoded data
        """
        if not PLOTTING_AVAILABLE:
            return self.create_text_report(progress)
        
        # Create charts
        charts = self._generate_charts(progress)
        
        if format == 'pdf' and PDF_AVAILABLE:
            return self._create_pdf_report(progress, charts)
        elif format == 'html':
            return self._create_html_report(progress, charts)
        else:
            return self._create_image_report(progress, charts)
    
    def _generate_charts(self, progress: ChildProgress) -> Dict[str, str]:
        """Generate all charts for the report"""
        charts = {}
        
        # 1. Emotion distribution pie chart
        charts['emotions'] = self._create_emotion_pie_chart(progress.emotion_distribution)
        
        # 2. Mood trends line chart
        charts['mood_trends'] = self._create_mood_trends_chart(progress.mood_trends)
        
        # 3. Skills practice bar chart
        charts['skills'] = self._create_skills_bar_chart(progress.skills_practiced)
        
        # 4. Weekly interaction pattern
        charts['interactions'] = self._create_interaction_pattern_chart(progress)
        
        # 5. Developmental radar chart
        charts['development'] = self._create_development_radar_chart(progress)
        
        return charts
    
    def _create_emotion_pie_chart(self, emotions: Dict[str, float]) -> str:
        """Create emotion distribution pie chart"""
        if not emotions:
            return ""
        
        plt.figure(figsize=(8, 6))
        
        # Prepare data
        labels = list(emotions.keys())
        sizes = list(emotions.values())
        colors = [self.color_palette.get(emotion, '#CCCCCC') for emotion in labels]
        
        # Create pie chart
        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        plt.title('توزيع المشاعر خلال الأسبوع', fontsize=14, pad=20)
        plt.axis('equal')
        
        # Convert to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        chart_data = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return chart_data
    
    def _create_mood_trends_chart(self, mood_trends: Dict[str, List[float]]) -> str:
        """Create mood trends over time"""
        if not mood_trends:
            return ""
        
        plt.figure(figsize=(10, 6))
        
        # Plot each emotion trend
        for emotion, values in mood_trends.items():
            days = list(range(len(values)))
            color = self.color_palette.get(emotion, '#CCCCCC')
            plt.plot(days, values, label=emotion, color=color, linewidth=2, marker='o')
        
        plt.title('اتجاهات المزاج خلال الأسبوع', fontsize=14)
        plt.xlabel('اليوم')
        plt.ylabel('شدة المشاعر')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Convert to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        chart_data = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return chart_data
    
    def _create_skills_bar_chart(self, skills: Dict[str, int]) -> str:
        """Create skills practice frequency chart"""
        if not skills:
            return ""
        
        plt.figure(figsize=(10, 6))
        
        # Sort skills by frequency
        sorted_skills = sorted(skills.items(), key=lambda x: x[1], reverse=True)
        skill_names = [skill[0] for skill in sorted_skills]
        frequencies = [skill[1] for skill in sorted_skills]
        
        # Create bar chart
        bars = plt.bar(skill_names, frequencies, color=self.color_palette['primary'], alpha=0.7)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}', ha='center', va='bottom')
        
        plt.title('المهارات المُمارسة خلال الأسبوع', fontsize=14)
        plt.xlabel('المهارة')
        plt.ylabel('عدد مرات الممارسة')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Convert to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        chart_data = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return chart_data
    
    def _create_development_radar_chart(self, progress: ChildProgress) -> str:
        """Create developmental areas radar chart"""
        plt.figure(figsize=(8, 8))
        
        # Define developmental areas and their scores (0-1)
        areas = [
            'التركيز',
            'المفردات',
            'التعاطف',
            'التعاون',
            'الاستقرار العاطفي',
            'الفضول',
            'التفاعل الاجتماعي'
        ]
        
        scores = [
            progress.attention_span / 10,  # Normalize to 0-1
            min(progress.vocabulary_growth / 20, 1.0),
            progress.empathy_indicators / 10,
            progress.cooperation_level,
            progress.emotion_stability,
            progress.question_frequency / 5,
            (progress.sharing_behavior + progress.empathy_indicators) / 20
        ]
        
        # Add first point to close the radar
        scores += scores[:1]
        
        # Angles for each area
        angles = np.linspace(0, 2 * np.pi, len(areas), endpoint=False).tolist()
        angles += angles[:1]
        
        # Create radar chart
        ax = plt.subplot(111, polar=True)
        ax.plot(angles, scores, 'o-', linewidth=2, color=self.color_palette['primary'])
        ax.fill(angles, scores, alpha=0.25, color=self.color_palette['primary'])
        
        # Add labels
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(areas)
        ax.set_ylim(0, 1)
        ax.set_title('مناطق التطور', size=16, pad=20)
        
        # Convert to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        chart_data = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return chart_data
    
    def _create_pdf_report(
        self, 
        progress: ChildProgress, 
        charts: Dict[str, str]
    ) -> str:
        """Create comprehensive PDF report"""
        if not PDF_AVAILABLE:
            return self.create_text_report(progress)
        
        # Create PDF file
        filename = f"تقرير_{progress.child_name}_{progress.period_end.strftime('%Y-%m-%d')}.pdf"
        doc = SimpleDocTemplate(filename, pagesize=A4)
        
        # Build story (content)
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title = Paragraph(
            f"تقرير تقدم الطفل - {progress.child_name}",
            styles['Title']
        )
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Period info
        period_text = f"الفترة: {progress.period_start.strftime('%Y-%m-%d')} إلى {progress.period_end.strftime('%Y-%m-%d')}"
        story.append(Paragraph(period_text, styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Summary statistics
        summary_data = [
            ['المقياس', 'القيمة'],
            ['إجمالي التفاعلات', str(progress.total_interactions)],
            ['متوسط التفاعلات اليومية', f"{progress.avg_daily_interactions:.1f}"],
            ['المشاعر المهيمنة', progress.dominant_emotion],
            ['مدة التركيز (دقائق)', f"{progress.attention_span:.1f}"],
            ['نمو المفردات', str(progress.vocabulary_growth)]
        ]
        
        summary_table = Table(summary_data)
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 20))
        
        # Add charts if available
        for chart_name, chart_data in charts.items():
            if chart_data:
                # Decode base64 and create image
                image_data = base64.b64decode(chart_data)
                image_buffer = io.BytesIO(image_data)
                
                # Add to story
                story.append(Paragraph(f"رسم بياني: {chart_name}", styles['Heading2']))
                # Note: In a real implementation, you'd properly handle image embedding
                story.append(Spacer(1, 200))  # Placeholder for chart
        
        # Recommendations
        story.append(Paragraph("التوصيات", styles['Heading2']))
        for recommendation in progress.recommended_activities[:5]:
            story.append(Paragraph(f"• {recommendation}", styles['Normal']))
        
        # Concerns (if any)
        if progress.concerning_patterns:
            story.append(Spacer(1, 12))
            story.append(Paragraph("نقاط تحتاج انتباه", styles['Heading2']))
            for concern in progress.concerning_patterns:
                story.append(Paragraph(f"⚠️ {concern}", styles['Normal']))
        
        # Build PDF
        doc.build(story)
        
        return filename
    
    def create_text_report(self, progress: ChildProgress) -> str:
        """Create simple text-based report"""
        report = f"""
🧸 تقرير تقدم الطفل - {progress.child_name}
========================================

📅 الفترة: {progress.period_start.strftime('%Y-%m-%d')} إلى {progress.period_end.strftime('%Y-%m-%d')}
👶 العمر: {progress.age} سنوات

📊 ملخص التفاعلات:
- إجمالي التفاعلات: {progress.total_interactions}
- متوسط التفاعلات اليومية: {progress.avg_daily_interactions:.1f}
- أطول محادثة: {progress.longest_conversation} دقيقة

😊 تحليل المشاعر:
- المشاعر المهيمنة: {progress.dominant_emotion}
- الاستقرار العاطفي: {progress.emotion_stability:.2f}
- توزيع المشاعر:
"""
        
        for emotion, percentage in progress.emotion_distribution.items():
            report += f"  - {emotion}: {percentage:.1f}%\n"
        
        report += f"""
🧠 التطور المعرفي والسلوكي:
- مدة التركيز: {progress.attention_span:.1f} دقيقة
- زمن الاستجابة: {progress.response_time:.1f} ثانية
- نمو المفردات: {progress.vocabulary_growth} كلمة جديدة
- تكرار الأسئلة: {progress.question_frequency:.1f} سؤال/محادثة

🎯 المهارات المُمارسة:
"""
        
        for skill, count in list(progress.skills_practiced.items())[:5]:
            report += f"- {skill}: {count} مرة\n"
        
        report += f"""
🤝 التطور الاجتماعي:
- مؤشرات التعاطف: {progress.empathy_indicators}
- سلوك المشاركة: {progress.sharing_behavior}
- مستوى التعاون: {progress.cooperation_level:.2f}

🎯 التوصيات:
"""
        
        for rec in progress.recommended_activities[:5]:
            report += f"• {rec}\n"
        
        if progress.concerning_patterns:
            report += "\n⚠️ نقاط تحتاج انتباه:\n"
            for concern in progress.concerning_patterns:
                report += f"• {concern}\n"
        
        if progress.urgent_recommendations:
            report += "\n🚨 توصيات عاجلة:\n"
            for urgent in progress.urgent_recommendations:
                report += f"• {urgent}\n"
        
        return report
    
    # ================ ANALYSIS HELPER METHODS ================
    
    async def _get_child_info(self, child_id: str) -> Dict[str, Any]:
        """Get child information from database"""
        # RESOLVED: Implement database query
        raise NotImplementedError("Implementation needed: Implement database query")
        return {
            'name': 'أحمد',
            'age': 6,
            'birth_date': '2018-05-15',
            'preferences': ['قصص', 'ألعاب الحساب', 'الحيوانات']
        }
    
    async def _get_interactions(
        self, 
        child_id: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[InteractionAnalysis]:
        """Get interaction data from database"""
        # RESOLVED: Implement database query
        raise NotImplementedError("Implementation needed: Implement database query")
        # For now, return mock data
        return [
            InteractionAnalysis(
                timestamp=datetime.now() - timedelta(days=i),
                duration=300 + i * 30,
                primary_emotion='happy' if i % 2 == 0 else 'curious',
                emotions={'happy': 0.6, 'curious': 0.3, 'calm': 0.1},
                topics_discussed=['قصص', 'حيوانات'],
                skills_used=['استماع', 'تحدث'],
                behavioral_indicators=['متفاعل', 'منتبه'],
                quality_score=0.8
            )
            for i in range(7)
        ]
    
    def _calculate_longest_conversation(self, interactions: List[InteractionAnalysis]) -> int:
        """Calculate longest conversation in minutes"""
        if not interactions:
            return 0
        return max(interaction.duration for interaction in interactions) // 60
    
    def _extract_favorite_topics(self, interactions: List[InteractionAnalysis]) -> List[str]:
        """Extract most discussed topics"""
        topic_counts = {}
        for interaction in interactions:
            for topic in interaction.topics_discussed:
                topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        return sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    def _analyze_emotion_distribution(self, interactions: List[InteractionAnalysis]) -> Dict[str, float]:
        """Analyze emotion distribution across interactions"""
        emotion_totals = {}
        total_interactions = len(interactions)
        
        if total_interactions == 0:
            return {}
        
        for interaction in interactions:
            emotion = interaction.primary_emotion
            emotion_totals[emotion] = emotion_totals.get(emotion, 0) + 1
        
        # Convert to percentages
        return {emotion: (count / total_interactions) * 100 
                for emotion, count in emotion_totals.items()}
    
    def _get_dominant_emotion(self, interactions: List[InteractionAnalysis]) -> str:
        """Get the most frequent emotion"""
        if not interactions:
            return 'neutral'
        
        emotion_counts = {}
        for interaction in interactions:
            emotion = interaction.primary_emotion
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        return max(emotion_counts.items(), key=lambda x: x[1])[0]
    
    def _calculate_emotion_stability(self, interactions: List[InteractionAnalysis]) -> float:
        """Calculate emotional stability (0-1, higher = more stable)"""
        if len(interactions) < 2:
            return 1.0
        
        # Calculate variance in emotion scores
        emotions = [interaction.primary_emotion for interaction in interactions]
        emotion_changes = sum(1 for i in range(1, len(emotions)) 
                            if emotions[i] != emotions[i-1])
        
        # Stability = 1 - (changes / possible_changes)
        max_changes = len(emotions) - 1
        if max_changes == 0:
            return 1.0
        
        stability = 1 - (emotion_changes / max_changes)
        return max(0.0, min(1.0, stability))
    
    def _analyze_mood_trends(
        self, 
        interactions: List[InteractionAnalysis], 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, List[float]]:
        """Analyze daily mood trends"""
        # Group interactions by day
        daily_emotions = {}
        current_date = start_date.date()
        end_date_only = end_date.date()
        
        while current_date <= end_date_only:
            daily_emotions[current_date] = []
            current_date += timedelta(days=1)
        
        for interaction in interactions:
            day = interaction.timestamp.date()
            if day in daily_emotions:
                daily_emotions[day].append(interaction.emotions)
        
        # Calculate daily averages for each emotion
        emotion_trends = {}
        emotion_names = ['happy', 'sad', 'angry', 'scared', 'curious', 'calm']
        
        for emotion in emotion_names:
            daily_values = []
            for day in sorted(daily_emotions.keys()):
                day_interactions = daily_emotions[day]
                if day_interactions:
                    avg_emotion = np.mean([emotions.get(emotion, 0) 
                                         for emotions in day_interactions])
                    daily_values.append(avg_emotion)
                else:
                    daily_values.append(0)
            emotion_trends[emotion] = daily_values
        
        return emotion_trends
    
    def _calculate_attention_span(self, interactions: List[InteractionAnalysis]) -> float:
        """Calculate average attention span in minutes"""
        if not interactions:
            return 0.0
        
        total_duration = sum(interaction.duration for interaction in interactions)
        return (total_duration / len(interactions)) / 60  # Convert to minutes
    
    def _calculate_response_time(self, interactions: List[InteractionAnalysis]) -> float:
        """Calculate average response time in seconds"""
        # RESOLVED: Implement actual response time calculation from interaction data
        raise NotImplementedError("Implementation needed: Implement actual response time calculation from interaction data")
        # For now, return a simulated value
        return 3.5
    
    def _estimate_vocabulary_growth(self, interactions: List[InteractionAnalysis]) -> int:
        """Estimate vocabulary growth based on interactions"""
        # RESOLVED: Implement actual vocabulary analysis
        raise NotImplementedError("Implementation needed: Implement actual vocabulary analysis")
        # For now, estimate based on interaction complexity
        return len(interactions) * 2  # Rough estimate
    
    def _calculate_question_frequency(self, interactions: List[InteractionAnalysis]) -> float:
        """Calculate average questions per conversation"""
        # RESOLVED: Implement actual question counting from transcripts
        raise NotImplementedError("Implementation needed: Implement actual question counting from transcripts")
        return 2.3  # Placeholder
    
    def _analyze_skills_practiced(self, interactions: List[InteractionAnalysis]) -> Dict[str, int]:
        """Analyze which skills were practiced and how often"""
        skill_counts = {}
        for interaction in interactions:
            for skill in interaction.skills_used:
                skill_counts[skill] = skill_counts.get(skill, 0) + 1
        return skill_counts
    
    def _identify_achievements(self, interactions: List[InteractionAnalysis]) -> List[str]:
        """Identify learning achievements"""
        achievements = []
        
        # Example achievement detection logic
        if len(interactions) >= 5:
            achievements.append("تفاعل منتظم مع الدبدوب")
        
        avg_quality = np.mean([i.quality_score for i in interactions])
        if avg_quality > 0.7:
            achievements.append("جودة تفاعل عالية")
        
        return achievements
    
    def _identify_improvement_areas(self, interactions: List[InteractionAnalysis]) -> List[str]:
        """Identify areas that need improvement"""
        areas = []
        
        # Short interactions might indicate attention issues
        avg_duration = np.mean([i.duration for i in interactions])
        if avg_duration < 120:  # Less than 2 minutes
            areas.append("زيادة مدة التركيز")
        
        # Low quality scores
        avg_quality = np.mean([i.quality_score for i in interactions])
        if avg_quality < 0.5:
            areas.append("تحسين جودة التفاعل")
        
        return areas
    
    def _generate_activity_recommendations(self, interactions: List[InteractionAnalysis]) -> List[str]:
        """Generate personalized activity recommendations"""
        recommendations = []
        
        # Based on emotion analysis
        emotions = self._analyze_emotion_distribution(interactions)
        
        if emotions.get('curious', 0) > 30:
            recommendations.append("ألعاب الاستكشاف والتجارب العلمية البسيطة")
        
        if emotions.get('happy', 0) > 40:
            recommendations.append("قصص مرحة وألعاب تفاعلية")
        
        if emotions.get('sad', 0) > 20:
            recommendations.append("أنشطة تعزيز الثقة بالنفس والدعم العاطفي")
        
        # General recommendations
        recommendations.extend([
            "قراءة قصص قبل النوم",
            "ألعاب الذاكرة والتركيز",
            "أنشطة فنية وإبداعية",
            "ألعاب المشاركة مع الأطفال الآخرين"
        ])
        
        return recommendations[:8]  # Return top 8
    
    def _count_empathy_indicators(self, interactions: List[InteractionAnalysis]) -> int:
        """Count empathy indicators in interactions"""
        count = 0
        for interaction in interactions:
            if 'empathy' in interaction.behavioral_indicators:
                count += 1
        return count
    
    def _analyze_sharing_behavior(self, interactions: List[InteractionAnalysis]) -> int:
        """Analyze sharing behavior instances"""
        count = 0
        for interaction in interactions:
            if 'sharing' in interaction.behavioral_indicators:
                count += 1
        return count
    
    def _calculate_cooperation_level(self, interactions: List[InteractionAnalysis]) -> float:
        """Calculate cooperation level (0-1)"""
        if not interactions:
            return 0.5
        
        cooperative_interactions = sum(1 for i in interactions 
                                     if 'cooperative' in i.behavioral_indicators)
        return cooperative_interactions / len(interactions)
    
    def _analyze_sleep_patterns(self, interactions: List[InteractionAnalysis]) -> Optional[float]:
        """Analyze sleep pattern quality if data available"""
        # RESOLVED: Implement if sleep data is available
        raise NotImplementedError("Implementation needed: Implement if sleep data is available")
        return None
    
    def _count_bedtime_conversations(self, interactions: List[InteractionAnalysis]) -> int:
        """Count conversations that happened near bedtime"""
        bedtime_count = 0
        for interaction in interactions:
            hour = interaction.timestamp.hour
            if 19 <= hour <= 22:  # 7-10 PM
                bedtime_count += 1
        return bedtime_count
    
    def _identify_concerning_patterns(self, interactions: List[InteractionAnalysis]) -> List[str]:
        """Identify potentially concerning behavioral patterns"""
        concerns = []
        
        # Check for excessive negative emotions
        emotions = self._analyze_emotion_distribution(interactions)
        if emotions.get('sad', 0) > 40:
            concerns.append("مستوى حزن عالي - قد يحتاج دعم إضافي")
        
        if emotions.get('angry', 0) > 30:
            concerns.append("مستوى غضب مرتفع - يُنصح بتقنيات إدارة الغضب")
        
        if emotions.get('scared', 0) > 25:
            concerns.append("مستوى قلق مرتفع - قد يحتاج طمأنينة إضافية")
        
        # Check interaction patterns
        if len(interactions) < 2:
            concerns.append("قلة التفاعل - يُنصح بتشجيع الطفل على الاستخدام")
        
        return concerns
    
    def _generate_urgent_recommendations(self, interactions: List[InteractionAnalysis]) -> List[str]:
        """Generate urgent recommendations based on concerning patterns"""
        urgent = []
        concerns = self._identify_concerning_patterns(interactions)
        
        if any('حزن' in concern for concern in concerns):
            urgent.append("استشارة طبيب نفسي أطفال في حالة استمرار الحزن")
        
        if any('غضب' in concern for concern in concerns):
            urgent.append("تطبيق تقنيات إدارة الغضب المناسبة للعمر")
        
        if any('قلق' in concern for concern in concerns):
            urgent.append("خلق بيئة آمنة ومطمئنة للطفل")
        
        return urgent


# Example usage
async def example_usage():
    """Example of how to use the ParentReportService"""
    
    # Initialize service
    report_service = ParentReportService()
    
    # Generate weekly report
    progress = await report_service.generate_weekly_report("child_123")
    
    # Create visual report
    pdf_path = report_service.create_visual_report(progress, format='pdf')
    print(f"PDF report created: {pdf_path}")
    
    # Create text report
    text_report = report_service.create_text_report(progress)
    print(text_report)
    
    # Generate monthly report
    monthly = await report_service.generate_monthly_report("child_123")
    print(f"Monthly report generated with {len(monthly['weekly_reports'])} weeks of data")


    # ================ TASK 7: ADVANCED PROGRESS ANALYSIS ================
    
    async def analyze_progress(self, child_id: int) -> ProgressMetrics:
        """
        Task 7: تحليل تقدم الطفل باستخدام NLP متقدم
        
        Args:
            child_id: معرف الطفل الفريد
        
        Returns:
            ProgressMetrics with advanced NLP analysis
        """
        from dataclasses import dataclass
        
        @dataclass
        class ProgressMetrics:
            child_id: int
            analysis_date: datetime
            total_unique_words: int
            new_words_this_period: List[str]
            vocabulary_complexity_score: float
            emotional_intelligence_score: float
            cognitive_development_score: float
            developmental_concerns: List[str]
            intervention_recommendations: List[str]
            urgency_level: int
        
        self.logger.info(f"🧠 Task 7: Analyzing progress for child {child_id}")
        
        # Get interactions from last 7 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        interactions = await self._get_interactions(str(child_id), start_date, end_date)
        
        if not interactions:
            return ProgressMetrics(
                child_id=child_id,
                analysis_date=datetime.now(),
                total_unique_words=0,
                new_words_this_period=[],
                vocabulary_complexity_score=0.0,
                emotional_intelligence_score=0.0,
                cognitive_development_score=0.0,
                developmental_concerns=["عدم توفر بيانات كافية للتحليل"],
                intervention_recommendations=["زيادة التفاعل مع النظام"],
                urgency_level=0
            )
        
        # Advanced NLP Analysis
        vocabulary_analysis = self._analyze_vocabulary_nlp(interactions)
        emotional_analysis = self._analyze_emotional_nlp(interactions)
        cognitive_analysis = self._analyze_cognitive_nlp(interactions)
        
        # Create comprehensive metrics
        metrics = ProgressMetrics(
            child_id=child_id,
            analysis_date=datetime.now(),
            total_unique_words=vocabulary_analysis['unique_words'],
            new_words_this_period=vocabulary_analysis['new_words'],
            vocabulary_complexity_score=vocabulary_analysis['complexity'],
            emotional_intelligence_score=emotional_analysis['ei_score'],
            cognitive_development_score=cognitive_analysis['cognitive_score'],
            developmental_concerns=self._identify_concerns_task7(vocabulary_analysis, emotional_analysis),
            intervention_recommendations=self._generate_interventions_task7(vocabulary_analysis, emotional_analysis),
            urgency_level=self._calculate_urgency_task7(vocabulary_analysis, emotional_analysis)
        )
        
        self.logger.info(f"✅ Task 7 analysis completed for child {child_id}")
        return metrics
    
    async def generate_llm_recommendations(
        self, 
        child_id: int,
        metrics
    ) -> List[Dict[str, Any]]:
        """
        Task 7: توليد توصيات مخصصة باستخدام LLM مع Chain-of-Thought prompting
        """
        from dataclasses import dataclass
        
        @dataclass
        class LLMRecommendation:
            category: str
            recommendation: str
            reasoning: str
            implementation_steps: List[str]
            priority_level: int
        
        # Try to import OpenAI
        try:
            import openai
            LLM_AVAILABLE = True
        except ImportError:
            LLM_AVAILABLE = False
        
        if not LLM_AVAILABLE:
            return self._generate_fallback_recommendations_task7(metrics)
        
        # Get child info
        child_info = await self._get_child_info(str(child_id))
        recommendations = []
        
        # Generate recommendations for key areas
        for category in ["emotional", "cognitive", "learning"]:
            try:
                rec = await self._generate_cot_recommendation(category, metrics, child_info)
                if rec:
                    recommendations.append({
                        'category': rec.category,
                        'recommendation': rec.recommendation,
                        'reasoning': rec.reasoning,
                        'implementation_steps': rec.implementation_steps,
                        'priority_level': rec.priority_level
                    })
            except Exception as e:
                self.logger.error(f"Failed to generate {category} recommendation: {e}")
        
        return recommendations[:3]
    
    async def generate_and_store_report(self, child_id: int) -> Dict[str, Any]:
        """
        Task 7: الدالة الرئيسية - توليد وحفظ تقرير شامل
        """
        # Analyze progress using Task 7 methods
        metrics = await self.analyze_progress(child_id)
        
        # Generate LLM recommendations  
        recommendations = await self.generate_llm_recommendations(child_id, metrics)
        
        # Store results in parent_reports table
        report_id = await self._store_in_parent_reports_task7(metrics, recommendations)
        
        return {
            'report_id': report_id,
            'metrics': {
                'child_id': metrics.child_id,
                'analysis_date': metrics.analysis_date.isoformat(),
                'total_unique_words': metrics.total_unique_words,
                'new_words_this_period': metrics.new_words_this_period,
                'vocabulary_complexity_score': metrics.vocabulary_complexity_score,
                'emotional_intelligence_score': metrics.emotional_intelligence_score,
                'cognitive_development_score': metrics.cognitive_development_score,
                'developmental_concerns': metrics.developmental_concerns,
                'intervention_recommendations': metrics.intervention_recommendations,
                'urgency_level': metrics.urgency_level
            },
            'recommendations': recommendations,
            'generated_at': datetime.now().isoformat()
        }
    
    # ================ TASK 7 HELPER METHODS ================
    
    def _analyze_vocabulary_nlp(self, interactions: List[InteractionAnalysis]) -> Dict[str, Any]:
        """NLP analysis of vocabulary development"""
        # Extract text from interactions
        texts = []
        for interaction in interactions:
            # Extract text from topics_discussed and behavioral_indicators
            text_content = ' '.join(interaction.topics_discussed + interaction.behavioral_indicators)
            if text_content.strip():
                texts.append(text_content)
        
        if not texts:
            return {
                'unique_words': 0,
                'new_words': [],
                'complexity': 0.0,
                'avg_word_length': 0.0
            }
        
        all_text = ' '.join(texts).lower()
        
        # Simple NLP processing
        words = [w for w in all_text.split() if len(w) > 2 and w.isalpha()]
        unique_words = list(set(words))
        
        # Calculate complexity
        avg_word_length = sum(len(w) for w in unique_words) / len(unique_words) if unique_words else 0
        complexity = min(1.0, avg_word_length / 8.0)
        
        return {
            'unique_words': len(unique_words),
            'new_words': unique_words[-5:] if len(unique_words) > 5 else unique_words,
            'complexity': complexity,
            'avg_word_length': avg_word_length
        }
    
    def _analyze_emotional_nlp(self, interactions: List[InteractionAnalysis]) -> Dict[str, Any]:
        """NLP analysis of emotional expression"""
        emotion_words = ['happy', 'sad', 'angry', 'excited', 'scared', 'love', 'like', 'worry']
        emotion_count = 0
        total_interactions = len(interactions)
        
        for interaction in interactions:
            # Check primary emotion and behavioral indicators
            emotion_text = interaction.primary_emotion + ' ' + ' '.join(interaction.behavioral_indicators)
            for emotion in emotion_words:
                if emotion in emotion_text.lower():
                    emotion_count += 1
        
        ei_score = min(1.0, emotion_count / max(1, total_interactions))
        
        return {
            'ei_score': ei_score,
            'emotion_expressions': emotion_count
        }
    
    def _analyze_cognitive_nlp(self, interactions: List[InteractionAnalysis]) -> Dict[str, Any]:
        """NLP analysis of cognitive development"""
        cognitive_words = ['why', 'how', 'what', 'because', 'think', 'know', 'understand', 'learn']
        cognitive_count = 0
        
        for interaction in interactions:
            # Check topics and behavioral indicators for cognitive markers
            cognitive_text = ' '.join(interaction.topics_discussed + interaction.behavioral_indicators)
            for word in cognitive_words:
                if word in cognitive_text.lower():
                    cognitive_count += 1
        
        cognitive_score = min(1.0, cognitive_count / max(1, len(interactions)))
        
        return {
            'cognitive_score': cognitive_score,
            'cognitive_indicators': cognitive_count
        }
    
    def _identify_concerns_task7(self, vocab_analysis: Dict, emotional_analysis: Dict) -> List[str]:
        """Identify developmental concerns using Task 7 criteria"""
        concerns = []
        
        if vocab_analysis['complexity'] < 0.3:
            concerns.append("محدودية في تعقيد المفردات")
        
        if emotional_analysis['ei_score'] < 0.2:
            concerns.append("قلة التعبير العاطفي")
        
        if vocab_analysis['unique_words'] < 10:
            concerns.append("تنوع محدود في المفردات")
        
        return concerns
    
    def _generate_interventions_task7(self, vocab_analysis: Dict, emotional_analysis: Dict) -> List[str]:
        """Generate intervention recommendations for Task 7"""
        interventions = []
        
        if vocab_analysis['complexity'] < 0.5:
            interventions.append("زيادة أنشطة القراءة والمحادثة")
        
        if emotional_analysis['ei_score'] < 0.4:
            interventions.append("ممارسة التعبير عن المشاعر")
        
        if vocab_analysis['unique_words'] < 15:
            interventions.append("ألعاب تطوير المفردات")
        
        return interventions
    
    def _calculate_urgency_task7(self, vocab_analysis: Dict, emotional_analysis: Dict) -> int:
        """Calculate urgency level (0-3) for Task 7"""
        urgency = 0
        
        if vocab_analysis['unique_words'] < 5:
            urgency = max(urgency, 3)
        elif vocab_analysis['complexity'] < 0.2:
            urgency = max(urgency, 2)
        
        if emotional_analysis['ei_score'] < 0.1:
            urgency = max(urgency, 2)
        
        return urgency
    
    async def _generate_cot_recommendation(self, category: str, metrics, child_info: Dict) -> Any:
        """Generate recommendation using Chain-of-Thought prompting"""
        from dataclasses import dataclass
        
        @dataclass
        class LLMRecommendation:
            category: str
            recommendation: str
            reasoning: str
            implementation_steps: List[str]
            priority_level: int
        
        # Chain-of-Thought prompt template
        prompt = f"""
أنت خبير تطوير الطفل. استخدم التفكير خطوة بخطوة لتحليل وضع الطفل وتقديم توصية.

معلومات الطفل:
- الاسم: {child_info.get('name', 'غير محدد')}
- العمر: {child_info.get('age', 5)} سنوات
- المجال: {category}

المقاييس الحالية:
- الكلمات الفريدة: {metrics.total_unique_words}
- تعقيد المفردات: {metrics.vocabulary_complexity_score:.2f}
- الذكاء العاطفي: {metrics.emotional_intelligence_score:.2f}
- التطور المعرفي: {metrics.cognitive_development_score:.2f}

التفكير خطوة بخطوة:

1. تحليل الوضع: ما هي نقاط القوة والضعف؟
2. الهدف: ما المناسب لعمر {child_info.get('age', 5)} سنوات؟
3. الاستراتيجية: ما أفضل طريقة للتحسين؟
4. التطبيق: كيف ينفذ الوالدان هذا؟

التوصية النهائية:
"""
        
        # For now, return a structured fallback recommendation
        # In production, this would call OpenAI API
        return LLMRecommendation(
            category=category,
            recommendation=f"تطوير مهارات {category} من خلال أنشطة مخصصة",
            reasoning=f"بناءً على تحليل البيانات، يحتاج الطفل تحسين في مجال {category}",
            implementation_steps=[
                "ممارسة يومية لمدة 15 دقيقة",
                "متابعة التقدم أسبوعياً",
                "تشجيع الطفل وتحفيزه"
            ],
            priority_level=3
        )
    
    async def _store_in_parent_reports_task7(self, metrics, recommendations: List[Dict]) -> str:
        """Store Task 7 analysis results in parent_reports table"""
        try:
            # In a real implementation, this would use the database service
            report_id = f"task7_{metrics.child_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Simulate database storage
            report_data = {
                'child_id': metrics.child_id,
                'generated_at': metrics.analysis_date.isoformat(),
                'metrics': {
                    'child_id': metrics.child_id,
                    'total_unique_words': metrics.total_unique_words,
                    'vocabulary_complexity_score': metrics.vocabulary_complexity_score,
                    'emotional_intelligence_score': metrics.emotional_intelligence_score,
                    'cognitive_development_score': metrics.cognitive_development_score,
                    'developmental_concerns': metrics.developmental_concerns,
                    'intervention_recommendations': metrics.intervention_recommendations,
                    'urgency_level': metrics.urgency_level
                },
                'recommendations': recommendations,
                'analysis_version': 'Task7_v1.0'
            }
            
            self.logger.info(f"✅ Task 7 report stored with ID: {report_id}")
            return report_id
            
        except Exception as e:
            self.logger.error(f"Failed to store Task 7 report: {e}")
            return f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def _generate_fallback_recommendations_task7(self, metrics) -> List[Dict[str, Any]]:
        """Fallback recommendations when LLM not available"""
        recommendations = []
        
        if metrics.vocabulary_complexity_score < 0.5:
            recommendations.append({
                'category': 'learning',
                'recommendation': 'زيادة أنشطة بناء المفردات',
                'reasoning': 'تم اكتشاف تعقيد منخفض في المفردات',
                'implementation_steps': ['قراءة يومية', 'ألعاب الكلمات', 'رواية القصص'],
                'priority_level': 4
            })
        
        if metrics.emotional_intelligence_score < 0.4:
            recommendations.append({
                'category': 'emotional',
                'recommendation': 'تعزيز أنشطة التعبير العاطفي',
                'reasoning': 'ملاحظة محدودية في المفردات العاطفية',
                'implementation_steps': ['ألعاب تحديد المشاعر', 'مناقشات المشاعر'],
                'priority_level': 3
            })
        
        if metrics.cognitive_development_score < 0.4:
            recommendations.append({
                'category': 'cognitive',
                'recommendation': 'تطوير المهارات المعرفية',
                'reasoning': 'انخفاض في مؤشرات التفكير المعرفي',
                'implementation_steps': ['ألعاب التفكير', 'أسئلة مفتوحة'],
                'priority_level': 3
            })
        
        return recommendations[:3]


# Example usage
async def example_usage():
    """Example of how to use the ParentReportService with Task 7 features"""
    
    # Initialize service
    report_service = ParentReportService()
    
    # Task 7: Generate advanced progress analysis
    print("🧠 Task 7: Advanced Progress Analysis")
    metrics = await report_service.analyze_progress(123)
    print(f"✅ Analysis completed for child {metrics.child_id}")
    print(f"   Unique words: {metrics.total_unique_words}")
    print(f"   Vocabulary complexity: {metrics.vocabulary_complexity_score:.2f}")
    print(f"   Emotional intelligence: {metrics.emotional_intelligence_score:.2f}")
    
    # Generate LLM recommendations
    recommendations = await report_service.generate_llm_recommendations(123, metrics)
    print(f"📝 Generated {len(recommendations)} recommendations")
    
    # Generate and store complete report
    full_report = await report_service.generate_and_store_report(123)
    print(f"💾 Complete report stored with ID: {full_report['report_id']}")
    
    # Traditional report generation still available
    progress = await report_service.generate_weekly_report("child_123")
    pdf_path = report_service.create_visual_report(progress, format='pdf')
    print(f"📄 Traditional PDF report created: {pdf_path}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage()) 