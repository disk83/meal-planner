from fastapi import APIRouter
from datetime import datetime, UTC

router = APIRouter()


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.get("/ping")
def ping():
    return {
        "status": "ok",
        "timestamp": datetime.now(UTC).isoformat(),
    }