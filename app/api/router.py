from fastapi import APIRouter

from app.api.requirements import router as requirements_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(requirements_router)
