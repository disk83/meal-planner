from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.meal_plan_service import generate_plan_service, generate_day_replacement_service

router = APIRouter()


class DayReplacementRequest(BaseModel):
    day: str
    current_recipe: str
    used_recipes: list[str] = Field(default_factory=list)


@router.post("/generate-plan")
async def generate_plan():
    return await generate_plan_service()


@router.post("/generate-day-replacement")
async def generate_day_replacement(payload: DayReplacementRequest):
    replacement = await generate_day_replacement_service(
        current_recipe=payload.current_recipe,
        used_recipes=payload.used_recipes,
    )

    if not replacement:
        raise HTTPException(status_code=400, detail="No replacement recipe available")

    return {"day": payload.day, "recipe": replacement}
