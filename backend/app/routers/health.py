from fastapi import APIRouter, Response
from datetime import datetime, UTC

router = APIRouter()


@router.get("/health")
async def health(response: Response):
    response.headers["X-Service-Name"] = "meal-planner"
    return {"status": "ok"}


@router.get("/ping")
def ping():
    return {
        "status": "ok",
        "timestamp": datetime.now(UTC).isoformat(),
    }

@router.get("/version")
def version():
    return {
        "version": "0.1",
        "timestamp": datetime.now(UTC).isoformat(),
    }
