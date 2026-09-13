from fastapi import APIRouter

from app.api.routes import datasets
from app.api.routes import health
from app.api.routes import upload

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(datasets.router)
api_router.include_router(upload.router)