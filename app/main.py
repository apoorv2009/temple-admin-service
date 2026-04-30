from fastapi import FastAPI

from app.api.router import api_router
from app.core.database import init_database

app = FastAPI(
    title="Temple Admin Service",
    version="0.1.0",
    summary="Admin approval workflow service for devotee onboarding.",
)
app.include_router(api_router)


@app.on_event("startup")
async def startup() -> None:
    init_database()
