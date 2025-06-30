"""
Notification Service
===================

Infrastructure service for sending notifications via email, SMS, and push.
"""

import aiosmtplib
import logging
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Template
from typing import Dict, Any, Optional


class NotificationService:
    """Service for sending various types of notifications"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.email_templates = self._load_email_templates()
    
    async def send_email_alert(
        self,
        recipient_email: str,
        alert_title: str,
        alert_message: str,
        child_name: str,
        alert_details: Dict[str, Any] = None
    ) -> bool:
        """Send email alert to parent"""
        
        try:
            # Render HTML content
            template = self.email_templates['alert']
            html_content = template.render(
                alert_title=alert_title,
                child_name=child_name,
                alert_message=alert_message,
                alert_details=alert_details or {},
                timestamp=datetime.now().strftime('%Y-%m-%d %I:%M %p')
            )
            
            # Create email
            msg = MIMEMultipart('alternative')
            msg['Subject'] = alert_title
            msg['From'] = self.config.get('EMAIL_FROM', 'noreply@ai-teddy.com')
            msg['To'] = recipient_email
            
            # Attach HTML
            msg.attach(MIMEText(html_content, 'html'))
            
            # Send email
            await self._send_smtp_email(msg)
            
            self.logger.info(f"Alert email sent to {recipient_email}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending email alert: {e}")
            return False
    
    async def send_daily_summary(
        self,
        recipient_email: str,
        child_name: str,
        summary_data: Dict[str, Any]
    ) -> bool:
        """Send daily summary email"""
        
        try:
            template = self.email_templates['daily_summary']
            html_content = template.render(
                child_name=child_name,
                date=datetime.now().strftime('%Y-%m-%d'),
                **summary_data
            )
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"Daily Summary for {child_name}"
            msg['From'] = self.config.get('EMAIL_FROM', 'noreply@ai-teddy.com')
            msg['To'] = recipient_email
            
            msg.attach(MIMEText(html_content, 'html'))
            
            await self._send_smtp_email(msg)
            
            self.logger.info(f"Daily summary sent to {recipient_email}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending daily summary: {e}")
            return False
    
    async def send_weekly_report(
        self,
        recipient_email: str,
        child_name: str,
        report_data: Dict[str, Any]
    ) -> bool:
        """Send weekly report email"""
        
        try:
            template = self.email_templates['weekly_report']
            html_content = template.render(
                child_name=child_name,
                week_start=report_data.get('week_start', ''),
                week_end=report_data.get('week_end', ''),
                **report_data
            )
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"Weekly Report for {child_name}"
            msg['From'] = self.config.get('EMAIL_FROM', 'noreply@ai-teddy.com')
            msg['To'] = recipient_email
            
            msg.attach(MIMEText(html_content, 'html'))
            
            await self._send_smtp_email(msg)
            
            self.logger.info(f"Weekly report sent to {recipient_email}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending weekly report: {e}")
            return False
    
    async def _send_smtp_email(self, message: MIMEMultipart) -> None:
        """Send email via SMTP"""
        
        smtp_config = {
            'hostname': self.config.get('SMTP_HOST', 'localhost'),
            'port': self.config.get('SMTP_PORT', 587),
            'use_tls': self.config.get('SMTP_USE_TLS', True)
        }
        
        async with aiosmtplib.SMTP(**smtp_config) as smtp:
            if smtp_config['use_tls']:
                await smtp.starttls()
            
            if self.config.get('SMTP_USER') and self.config.get('SMTP_PASS'):
                await smtp.login(
                    self.config['SMTP_USER'],
                    self.config['SMTP_PASS']
                )
            
            await smtp.send_message(message)
    
    def _load_email_templates(self) -> Dict[str, Template]:
        """Load email templates"""
        
        templates = {
            'alert': Template("""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="utf-8">
                    <title>{{ alert_title }}</title>
                    <style>
                        body { font-family: Arial, sans-serif; line-height: 1.6; }
                        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                        .header { background: #e74c3c; color: white; padding: 20px; text-align: center; }
                        .content { padding: 20px; background: #f9f9f9; }
                        .footer { padding: 20px; text-align: center; color: #666; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h1>{{ alert_title }}</h1>
                        </div>
                        <div class="content">
                            <h2>Alert for {{ child_name }}</h2>
                            <p><strong>Time:</strong> {{ timestamp }}</p>
                            <p><strong>Message:</strong> {{ alert_message }}</p>
                            {% if alert_details %}
                            <h3>Details:</h3>
                            <ul>
                                {% for key, value in alert_details.items() %}
                                <li><strong>{{ key }}:</strong> {{ value }}</li>
                                {% endfor %}
                            </ul>
                            {% endif %}
                        </div>
                        <div class="footer">
                            <p>AI Teddy Bear Parent Dashboard</p>
                        </div>
                    </div>
                </body>
                </html>
            """),
            
            'daily_summary': Template("""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="utf-8">
                    <title>Daily Summary for {{ child_name }}</title>
                    <style>
                        body { font-family: Arial, sans-serif; line-height: 1.6; }
                        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                        .header { background: #3498db; color: white; padding: 20px; text-align: center; }
                        .content { padding: 20px; }
                        .stat { margin: 10px 0; padding: 10px; background: #ecf0f1; border-radius: 5px; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h1>Daily Summary for {{ child_name }}</h1>
                            <p>{{ date }}</p>
                        </div>
                        <div class="content">
                            <div class="stat">
                                <strong>Total Conversations:</strong> {{ total_conversations | default(0) }}
                            </div>
                            <div class="stat">
                                <strong>Total Time:</strong> {{ total_time | default(0) }} minutes
                            </div>
                            <div class="stat">
                                <strong>Topics Discussed:</strong> {{ topics | join(', ') if topics else 'None' }}
                            </div>
                            <div class="stat">
                                <strong>Overall Sentiment:</strong> {{ sentiment | default('Neutral') }}
                            </div>
                        </div>
                    </div>
                </body>
                </html>
            """),
            
            'weekly_report': Template("""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="utf-8">
                    <title>Weekly Report for {{ child_name }}</title>
                    <style>
                        body { font-family: Arial, sans-serif; line-height: 1.6; }
                        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                        .header { background: #27ae60; color: white; padding: 20px; text-align: center; }
                        .content { padding: 20px; }
                        .section { margin: 20px 0; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h1>Weekly Report for {{ child_name }}</h1>
                            <p>{{ week_start }} - {{ week_end }}</p>
                        </div>
                        <div class="content">
                            <div class="section">
                                <h2>Activity Summary</h2>
                                <p><strong>Total Conversations:</strong> {{ total_conversations | default(0) }}</p>
                                <p><strong>Total Time:</strong> {{ total_hours | default(0) }} hours</p>
                                <p><strong>Average Session:</strong> {{ avg_session | default(0) }} minutes</p>
                            </div>
                            <div class="section">
                                <h2>Learning Progress</h2>
                                <p><strong>Educational Engagement:</strong> {{ educational_engagement | default('No data') }}</p>
                                <p><strong>Vocabulary Growth:</strong> {{ vocabulary_growth | default(0) }} new words</p>
                            </div>
                        </div>
                    </div>
                </body>
                </html>
            """)
        }
        
        return templates 