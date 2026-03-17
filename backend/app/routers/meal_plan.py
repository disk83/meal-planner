from fastapi import APIRouter

from app.services.meal_plan_service import generate_plan_service

router = APIRouter()

@router.post("/generate-plan")
async def generate_plan():
    return await generate_plan_service()