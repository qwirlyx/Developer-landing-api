import asyncio
import html
import json
import os
import smtplib
from datetime import datetime
from email.message import EmailMessage

from app.config import get_settings
from app.core.logger import logger


class EmailService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.outbox_file = os.path.join("app", "storage", "email_outbox.json")

    async def send_contact_emails(
        self,
        name: str,
        phone: str,
        email: str,
        comment: str,
        ai_result: dict,
    ) -> dict:
        owner_subject = "Новая заявка с лендинга"
        owner_text = self._build_owner_text(name, phone, email, comment, ai_result)
        owner_html = self._build_owner_html(name, phone, email, comment, ai_result)

        user_subject = "Ваша заявка получена"
        user_text = self._build_user_text(name)
        user_html = self._build_user_html(name)

        owner_status = await asyncio.to_thread(
            self._send_email,
            self.settings.owner_email,
            owner_subject,
            owner_text,
            owner_html,
        )

        user_status = await asyncio.to_thread(
            self._send_email,
            email,
            user_subject,
            user_text,
            user_html,
        )

        return {
            "owner_email_sent": owner_status,
            "user_email_sent": user_status,
        }

    def _is_configured(self) -> bool:
        return all(
            [
                self.settings.smtp_host,
                self.settings.smtp_username,
                self.settings.smtp_password,
                self.settings.smtp_from_email,
                self.settings.owner_email,
            ]
        )

    def _send_email(
        self,
        to_email: str,
        subject: str,
        text_body: str,
        html_body: str | None = None,
    ) -> bool:
        self._save_to_outbox(to_email, subject, text_body, html_body)

        if not self._is_configured():
            logger.warning("SMTP is not configured. Email was saved to outbox only.")
            return False

        try:
            message = EmailMessage()
            message["Subject"] = subject
            message["From"] = self.settings.smtp_from_email
            message["To"] = to_email

            message.set_content(text_body)

            if html_body:
                message.add_alternative(html_body, subtype="html")

            with smtplib.SMTP(
                self.settings.smtp_host,
                self.settings.smtp_port,
                timeout=20,
            ) as server:
                if self.settings.smtp_use_tls:
                    server.starttls()

                server.login(
                    self.settings.smtp_username,
                    self.settings.smtp_password,
                )
                server.send_message(message)

            logger.info("Email sent successfully to %s", to_email)
            return True

        except Exception as error:
            logger.exception("Email sending failed to %s: %s", to_email, str(error))
            return False

    def _build_owner_text(
        self,
        name: str,
        phone: str,
        email: str,
        comment: str,
        ai_result: dict,
    ) -> str:
        ai = self._extract_ai_result(ai_result)

        return (
            "Получена новая заявка с лендинга.\n\n"
            f"Имя: {name}\n"
            f"Телефон: {phone}\n"
            f"Email: {email}\n\n"
            f"Комментарий:\n{comment}\n\n"
            "AI-анализ:\n"
            f"Категория: {ai['category']}\n"
            f"Тональность: {ai['tone']}\n"
            f"Приоритет: {ai['priority']}\n"
            f"Вариант ответа: {ai['suggested_reply']}\n"
        )

    def _build_owner_html(
        self,
        name: str,
        phone: str,
        email: str,
        comment: str,
        ai_result: dict,
    ) -> str:
        ai = self._extract_ai_result(ai_result)

        safe_name = html.escape(name)
        safe_phone = html.escape(phone)
        safe_email = html.escape(email)
        safe_comment = html.escape(comment)
        safe_category = html.escape(ai["category"])
        safe_tone = html.escape(ai["tone"])
        safe_priority = html.escape(ai["priority"])
        safe_reply = html.escape(ai["suggested_reply"])

        return f"""
        <!doctype html>
        <html lang="ru">
        <body style="margin:0;padding:0;background:#f4f6f8;font-family:Arial,sans-serif;color:#1f2937;">
          <div style="max-width:640px;margin:0 auto;padding:24px;">
            <div style="background:#ffffff;border:1px solid #e5e7eb;border-radius:16px;padding:24px;">
              <p style="margin:0 0 8px;font-size:13px;color:#6b7280;">Developer Landing API</p>
              <h1 style="margin:0 0 20px;font-size:24px;line-height:1.25;color:#111827;">
                Новая заявка с лендинга
              </h1>

              <div style="margin-bottom:20px;padding:16px;background:#f9fafb;border-radius:12px;">
                <p style="margin:0 0 8px;"><strong>Имя:</strong> {safe_name}</p>
                <p style="margin:0 0 8px;"><strong>Телефон:</strong> {safe_phone}</p>
                <p style="margin:0;"><strong>Email:</strong> {safe_email}</p>
              </div>

              <h2 style="margin:0 0 10px;font-size:16px;color:#111827;">Комментарий</h2>
              <p style="margin:0 0 20px;line-height:1.6;">{safe_comment}</p>

              <h2 style="margin:0 0 10px;font-size:16px;color:#111827;">AI-анализ</h2>
              <div style="padding:16px;background:#eef6ff;border-radius:12px;border:1px solid #dbeafe;">
                <p style="margin:0 0 8px;"><strong>Категория:</strong> {safe_category}</p>
                <p style="margin:0 0 8px;"><strong>Тональность:</strong> {safe_tone}</p>
                <p style="margin:0 0 8px;"><strong>Приоритет:</strong> {safe_priority}</p>
                <p style="margin:0;line-height:1.6;"><strong>Вариант ответа:</strong> {safe_reply}</p>
              </div>
            </div>
          </div>
        </body>
        </html>
        """

    def _build_user_text(self, name: str) -> str:
        return (
            f"Здравствуйте, {name}!\n\n"
            "Ваша заявка успешно получена.\n"
            "Это автоматическое письмо от тестового backend API.\n\n"
            "С уважением,\n"
            "Developer Landing API"
        )

    def _build_user_html(self, name: str) -> str:
        safe_name = html.escape(name)

        return f"""
        <!doctype html>
        <html lang="ru">
        <body style="margin:0;padding:0;background:#f4f6f8;font-family:Arial,sans-serif;color:#1f2937;">
          <div style="max-width:560px;margin:0 auto;padding:24px;">
            <div style="background:#ffffff;border:1px solid #e5e7eb;border-radius:16px;padding:24px;">
              <p style="margin:0 0 8px;font-size:13px;color:#6b7280;">Developer Landing API</p>
              <h1 style="margin:0 0 16px;font-size:24px;line-height:1.25;color:#111827;">
                Заявка получена
              </h1>
              <p style="margin:0 0 12px;line-height:1.6;">
                Здравствуйте, {safe_name}!
              </p>
              <p style="margin:0 0 12px;line-height:1.6;">
                Ваша заявка успешно отправлена и принята в обработку.
              </p>
              <p style="margin:0;line-height:1.6;color:#6b7280;">
                Это автоматическое письмо от тестового backend API.
              </p>
            </div>
          </div>
        </body>
        </html>
        """

    def _extract_ai_result(self, ai_result: dict) -> dict:
        result = ai_result.get("result", {}) if isinstance(ai_result, dict) else {}

        return {
            "category": str(result.get("category", "other")),
            "tone": str(result.get("tone", "neutral")),
            "priority": str(result.get("priority", "medium")),
            "suggested_reply": str(
                result.get(
                    "suggested_reply",
                    "Спасибо за обращение. Я свяжусь с вами после обработки заявки.",
                )
            ),
        }

    def _save_to_outbox(
        self,
        to_email: str,
        subject: str,
        text_body: str,
        html_body: str | None = None,
    ) -> None:
        os.makedirs(os.path.dirname(self.outbox_file), exist_ok=True)

        try:
            if os.path.exists(self.outbox_file):
                with open(self.outbox_file, "r", encoding="utf-8") as file:
                    outbox = json.load(file)
            else:
                outbox = []

            outbox.append(
                {
                    "created_at": datetime.utcnow().isoformat(),
                    "to": to_email,
                    "subject": subject,
                    "text_body": text_body,
                    "html_body": html_body,
                }
            )

            with open(self.outbox_file, "w", encoding="utf-8") as file:
                json.dump(outbox, file, ensure_ascii=False, indent=2)

        except Exception as error:
            logger.exception("Failed to save email to outbox: %s", str(error))
