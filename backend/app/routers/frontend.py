from fastapi import APIRouter
from fastapi.responses import FileResponse

from app.config import FRONTEND_DIR

router = APIRouter()

@router.get("/")
async def serve_frontend():
    return FileResponse(str(FRONTEND_DIR / "index.html"))