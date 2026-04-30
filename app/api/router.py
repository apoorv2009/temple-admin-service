from fastapi import APIRouter

from app.api.routes import admin_requests, health, temples

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(
    temples.router,
    prefix="/api/v1/temples",
    tags=["temples"],
)
api_router.include_router(
    admin_requests.router,
    prefix="/api/v1/admin/temple-subscriptions",
    tags=["admin-temple-subscriptions"],
)
