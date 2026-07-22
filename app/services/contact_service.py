from app.repositories.file_repository import FileRepository
from app.schemas.contact import ContactRequest
from app.services.ai_service import AIService
from app.services.email_service import EmailService


class ContactService:
    def __init__(self) -> None:
        self.ai_service = AIService()
        self.email_service = EmailService()
        self.repository = FileRepository()

    async def process_contact(self, payload: ContactRequest) -> dict:
        self.repository.increment_metric("total_requests")

        ai_result = await self.ai_service.analyze_comment(payload.comment)

        if ai_result.get("status") == "success":
            self.repository.increment_metric("ai_success")
        else:
            self.repository.increment_metric("ai_fallback")

        email_result = await self.email_service.send_contact_emails(
            name=payload.name,
            phone=payload.phone,
            email=str(payload.email),
            comment=payload.comment,
            ai_result=ai_result,
        )

        self.repository.increment_metric("successful_requests")

        return {
            "status": "success",
            "message": "Заявка успешно обработана",
            "ai": ai_result,
            "email": email_result,
        }