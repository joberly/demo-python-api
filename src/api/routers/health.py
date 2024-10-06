from fastapi import APIRouter

from .routers import routers

router = APIRouter()

# Health check endpoint

@router.get("/health/")
async def health():
    return { "status": "ok" }

routers.append(router)
