import asyncio
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
        storage_dir = os.getenv(
            "STORAGE_DIR",
            os.path.join("app", "storage"),
        )
        
        self.outbox_file = os.path.join(storage_dir, "email_outbox.json")

    async def send_contact_emails(
        self,
        name: str,
        phone: str,
        email: str,
        comment: str,
        ai_result: dict,
    ) -> dict:
        owner_subject = "Новая заявка с формы обратной связи"
        owner_body = (
            "Получена новая заявка через backend API.\n\n"
            f"Имя: {name}\n"
            f"Телефон: {phone}\n"
            f"Email: {email}\n\n"
            f"Комментарий:\n{comment}\n\n"
            f"AI-анализ:\n{ai_result}\n"
        )

        user_subject = "Ваша заявка получена"
        user_body = (
            f"Здравствуйте, {name}!\n\n"
            "Ваша заявка успешно получена.\n"
            "Это автоматическое письмо от тестового backend API.\n\n"
            "Если вы видите это письмо в локальном outbox, значит email-сервис сформировал сообщение корректно.\n\n"
            "С уважением,\n"
            "Developer Landing API"
        )

        owner_status = await asyncio.to_thread(
            self._send_email,
            self.settings.owner_email,
            owner_subject,
            owner_body,
        )

        user_status = await asyncio.to_thread(
            self._send_email,
            email,
            user_subject,
            user_body,
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

    def _send_email(self, to_email: str, subject: str, body: str) -> bool:
        self._save_to_outbox(to_email, subject, body)

        if not self._is_configured():
            logger.warning("SMTP is not configured. Email was saved to outbox only.")
            return False

        try:
            message = EmailMessage()
            message["Subject"] = subject
            message["From"] = self.settings.smtp_from_email
            message["To"] = to_email
            message.set_content(body)

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

    def _save_to_outbox(self, to_email: str, subject: str, body: str) -> None:
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
                    "body": body,
                }
            )

            with open(self.outbox_file, "w", encoding="utf-8") as file:
                json.dump(outbox, file, ensure_ascii=False, indent=2)

        except Exception as error:
            logger.exception("Failed to save email to outbox: %s", str(error))
