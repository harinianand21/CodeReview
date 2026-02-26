from typing import Any
from fastapi import APIRouter

router = APIRouter()

@router.get("/health", response_model=dict[str, str])
def health_check() -> Any:
    """
    Health check endpoint to ensure the service is running.
    
    Returns:
        dict: A dictionary containing the status "ok".
    """
    return {"status": "ok"}
