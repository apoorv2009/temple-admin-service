from fastapi import APIRouter

from app.api.routes import admin_requests, health

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(
    admin_requests.router,
    prefix="/api/v1/admin/signup-requests",
    tags=["admin-signup-requests"],
)

