import os
import time

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.contact import router as contact_router
from app.config import get_settings
from app.core.exceptions import AppException
from app.core.logger import logger
from app.repositories.file_repository import FileRepository

settings = get_settings()
repository = FileRepository()

app = FastAPI(
    title=settings.app_name,
    description="Backend API for developer landing page with AI integration.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if os.path.isdir("frontend"):
    app.mount("/static", StaticFiles(directory="frontend"), name="static")


    @app.get("/", include_in_schema=False)
    async def landing_page():
        return FileResponse("frontend/index.html")


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    start_time = time.time()

    try:
        response = await call_next(request)
        process_time = round(time.time() - start_time, 4)

        logger.info(
            "%s %s | status=%s | ip=%s | time=%ss",
            request.method,
            request.url.path,
            response.status_code,
            request.client.host if request.client else "unknown",
            process_time,
        )

        return response

    except Exception as error:
        process_time = round(time.time() - start_time, 4)

        logger.exception(
            "%s %s | unhandled_error=%s | ip=%s | time=%ss",
            request.method,
            request.url.path,
            str(error),
            request.client.host if request.client else "unknown",
            process_time,
        )

        repository.increment_metric("failed_requests")

        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Internal server error",
            },
        )


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    repository.increment_metric("failed_requests")

    logger.warning(
        "%s %s | app_error=%s | status=%s",
        request.method,
        request.url.path,
        exc.message,
        exc.status_code,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.message,
        },
    )


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    repository.increment_metric("failed_requests")

    errors = []

    for error in exc.errors():
        prepared_error = {
            "field": ".".join(str(item) for item in error.get("loc", [])),
            "message": error.get("msg"),
            "type": error.get("type"),
        }
        errors.append(prepared_error)

    logger.warning(
        "%s %s | validation_error=%s",
        request.method,
        request.url.path,
        errors,
    )

    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "message": "Validation error",
            "details": errors,
        },
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    repository.increment_metric("failed_requests")

    logger.warning(
        "%s %s | http_error=%s | status=%s",
        request.method,
        request.url.path,
        exc.detail,
        exc.status_code,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.detail,
        },
    )


app.include_router(contact_router, prefix=settings.api_prefix)