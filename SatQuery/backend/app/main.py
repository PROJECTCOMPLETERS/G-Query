import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.exceptions import (
    SatQueryException,
    satquery_exception_handler,
)
from app.api.router import api_router


setup_logging()

logger = logging.getLogger("satquery")

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Satellite Query and Analysis API",
)

app.add_exception_handler(
    SatQueryException,
    satquery_exception_handler,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/api/health")
def health_check():
    logger.info("Health check requested")

    return {
        "success": True,
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "healthy",
    }