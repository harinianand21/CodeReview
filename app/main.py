from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings

def get_application() -> FastAPI:
    """
    Initialize and configure the FastAPI application.
    """
    _app = FastAPI(
        title=settings.APP_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        debug=settings.DEBUG
    )

    # Set all CORS enabled origins
    if settings.ALLOWED_HOSTS:
        _app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.ALLOWED_HOSTS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Include API router
    _app.include_router(api_router, prefix=settings.API_V1_STR)

    return _app

app = get_application()

@app.get("/", tags=["root"])
async def root() -> dict[str, str]:
    """
    Root endpoint returning basic application info.
    """
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": "1.0.0",
        "docs": "/docs"
    }
