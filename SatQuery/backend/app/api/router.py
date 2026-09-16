from fastapi import APIRouter

from app.api.routes import datasets
from app.api.routes import health
from app.api.routes import upload
from app.api.routes import query
from app.api.routes import reference
from app.api.routes import tiles

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(datasets.router)
api_router.include_router(upload.router)
api_router.include_router(query.router)
api_router.include_router(tiles.router)