from fastapi import APIRouter, Request

from app.repositories.file_repository import FileRepository
from app.schemas.contact import ContactRequest, ContactResponse
from app.services.contact_service import ContactService
from app.services.rate_limit_service import RateLimitService

router = APIRouter()

contact_service = ContactService()
rate_limit_service = RateLimitService()
repository = FileRepository()


@router.post("/contact", response_model=ContactResponse)
async def create_contact_request(
    payload: ContactRequest,
    request: Request,
) -> dict:
    client_ip = request.client.host if request.client else "unknown"

    rate_limit_service.check(client_ip)

    return await contact_service.process_contact(payload)


@router.get("/health")
async def health_check() -> dict:
    return {
        "status": "ok",
        "service": "Developer Landing API",
    }


@router.get("/metrics")
async def get_metrics() -> dict:
    return repository.get_metrics()