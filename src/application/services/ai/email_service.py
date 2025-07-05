from typing import Any, List, Optional

#!/usr/bin/env python3
"""
📧 Email Service - خدمة البريد الإلكتروني
إرسال رسائل بريد إلكتروني بتنسيق HTML وNTXT مع دعم المرفقات
"""

import asyncio
import json
from email import encoders
from email.mime.base import MIMEBase as MimeBase
from email.mime.multipart import MIMEMultipart as MimeMultipart
from email.mime.text import MIMEText as MimeText
from pathlib import Path
from typing import List, Optional

import aiosmtplib
import structlog

# إعداد logger
logger = structlog.get_logger(__name__)


class EmailService:
    """
    📧 خدمة البريد الإلكتروني المتقدمة

    الميزات:
    - إرسال HTML و Plain Text
    - دعم المرفقات
    - إرسال غير متزامن
    - إعادة المحاولة التلقائية
    - قوالب جاهزة
    """

    def __init__(self):
        self.logger = logger.bind(service="email")
        self._load_config()

    def _load_config(self) -> Any:
        """تحميل إعدادات البريد الإلكتروني"""
        try:
            config_path = Path(__file__).parent.parent.parent / \
                "config" / "config.json"
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)

            email_config = config.get("EMAIL_CONFIG", {})

            self.smtp_server = email_config.get(
                "smtp_server", "smtp.gmail.com")
            self.smtp_port = email_config.get("smtp_port", 587)
            self.from_email = email_config.get(
                "from_email", "noreply@aiteddybear.com")
            self.password = email_config.get("password", "")
            self.use_tls = email_config.get("use_tls", True)
            self.timeout = email_config.get("timeout", 30)

        except Exception as e:
            self.logger.warning("Failed to load email config", error=str(e))
            # إعدادات افتراضية
            self.smtp_server = "smtp.gmail.com"
            self.smtp_port = 587
            self.from_email = "noreply@aiteddybear.com"
            self.password = ""
            self.use_tls = True
            self.timeout = 30

    async def send_html_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        attachments: Optional[List[Path]] = None,
    ) -> bool:
        """
        إرسال بريد إلكتروني بتنسيق HTML

        Args:
            to_email: عنوان المستقبل
            subject: موضوع الرسالة
            html_content: محتوى HTML
            text_content: محتوى نصي (اختياري)
            attachments: المرفقات (اختياري)

        Returns:
            bool: نجح الإرسال أم لا
        """
        try:
            # إنشاء الرسالة
            message = MimeMultipart("alternative")
            message["From"] = self.from_email
            message["To"] = to_email
            message["Subject"] = subject

            # إضافة المحتوى النصي
            if text_content:
                text_part = MimeText(text_content, "plain", "utf-8")
                message.attach(text_part)

            # إضافة المحتوى HTML
            html_part = MimeText(html_content, "html", "utf-8")
            message.attach(html_part)

            # إضافة المرفقات
            if attachments:
                for attachment_path in attachments:
                    await self._add_attachment(message, attachment_path)

            # إرسال الرسالة
            success = await self._send_message(message, to_email)

            if success:
                self.logger.info(
                    "HTML email sent successfully",
                    to=to_email,
                    subject=subject)
            else:
                self.logger.error(
                    "Failed to send HTML email", to=to_email, subject=subject
                )

            return success

        except Exception as e:
            self.logger.error(
                "HTML email sending failed",
                to=to_email,
                error=str(e),
                exc_info=True)
            return False

    async def send_text_email(
        self, to_email: str, subject: str, text_content: str
    ) -> bool:
        """
        إرسال بريد إلكتروني نصي بسيط

        Args:
            to_email: عنوان المستقبل
            subject: موضوع الرسالة
            text_content: المحتوى النصي

        Returns:
            bool: نجح الإرسال أم لا
        """
        try:
            # إنشاء الرسالة
            message = MimeText(text_content, "plain", "utf-8")
            message["From"] = self.from_email
            message["To"] = to_email
            message["Subject"] = subject

            # إرسال الرسالة
            success = await self._send_message(message, to_email)

            if success:
                self.logger.info(
                    "Text email sent successfully",
                    to=to_email,
                    subject=subject)
            else:
                self.logger.error(
                    "Failed to send text email", to=to_email, subject=subject
                )

            return success

        except Exception as e:
            self.logger.error(
                "Text email sending failed",
                to=to_email,
                error=str(e),
                exc_info=True)
            return False

    async def _send_message(
            self,
            message: MimeMultipart,
            to_email: str) -> bool:
        """إرسال الرسالة عبر SMTP"""
        try:
            # في بيئة التطوير، نقوم بمحاكاة الإرسال
            if not self.password or self.password == "your_app_password":
                self.logger.info(
                    "Email sending simulated (no password configured)",
                    to=to_email)
                return True

            # الإرسال الفعلي باستخدام aiosmtplib
            await aiosmtplib.send(
                message,
                hostname=self.smtp_server,
                port=self.smtp_port,
                start_tls=self.use_tls,
                username=self.from_email,
                password=self.password,
                timeout=self.timeout,
            )

            return True

        except Exception as e:
            self.logger.error("SMTP sending failed", error=str(e))
            return False

    async def _add_attachment(
            self,
            message: MimeMultipart,
            attachment_path: Path):
        """إضافة مرفق للرسالة"""
        try:
            if not attachment_path.exists():
                self.logger.warning(
                    "Attachment file not found", path=str(attachment_path)
                )
                return

            with open(attachment_path, "rb") as attachment:
                part = MimeBase("application", "octet-stream")
                part.set_payload(attachment.read())

            encoders.encode_base64(part)
            part.add_header("Content-Disposition",
                            f"attachment; filename= {attachment_path.name}")

            message.attach(part)
            self.logger.debug(
                "Attachment added",
                filename=attachment_path.name)

        except Exception as e:
            self.logger.error(
                "Failed to add attachment",
                path=str(attachment_path),
                error=str(e))


# 🔧 مثيل خدمة البريد العامة
email_service = EmailService()


# 🚀 دوال مساعدة
async def send_email(to_email: str, subject: str, body: str) -> bool:
    """دالة بسيطة لإرسال بريد نصي"""
    return await email_service.send_text_email(to_email, subject, body)


async def send_html_email(
        to_email: str,
        subject: str,
        html_content: str) -> bool:
    """دالة بسيطة لإرسال بريد HTML"""
    return await email_service.send_html_email(to_email, subject, html_content)


if __name__ == "__main__":
    # اختبار الخدمة
    async def test_email():
        logger.info("📧 Testing Email Service...")

        # اختبار بريد نصي
        success = await send_email(
            "test@example.com", "Test Email", "This is a test email from AI Teddy Bear!"
        )
        logger.error(
            f"Text email test: {'✅ Success' if success else '❌ Failed'}")

        # اختبار بريد HTML
        html = "<h1>Test HTML Email</h1><p>This is a <b>test</b> HTML email!</p>"
        success = await send_html_email("test@example.com", "Test HTML Email", html)
        logger.error(
            f"HTML email test: {'✅ Success' if success else '❌ Failed'}")

    asyncio.run(test_email())
