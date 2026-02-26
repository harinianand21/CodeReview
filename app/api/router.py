from fastapi import APIRouter
from app.api.v1 import health

api_router = APIRouter()

# Include health check router
api_router.include_router(health.router, tags=["health"])

# Placeholder for other module routers
# api_router.include_router(analyzer_router, prefix="/analyze", tags=["analysis"])
# api_router.include_router(score_router, prefix="/score", tags=["scoring"])
