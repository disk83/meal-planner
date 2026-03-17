from fastapi import APIRouter

from app.config import AVAILABLE_TAGS

router = APIRouter()

@router.get("/tags")
async def get_tags():
    return AVAILABLE_TAGS