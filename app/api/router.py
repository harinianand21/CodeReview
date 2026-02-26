from fastapi import APIRouter
from app.api.v1 import health, analyze

api_router = APIRouter()

# Include health check router
api_router.include_router(health.router, tags=["health"])

# Include repository analysis router
api_router.include_router(analyze.router, tags=["analysis"])
