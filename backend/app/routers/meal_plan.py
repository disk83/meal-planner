from datetime import date as dt_date

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.meal_plan_service import (
    generate_and_save_meal_plan_for_date_service,
    generate_day_replacement_service,
    generate_plan_service,
    get_meal_plan_for_date_service,
)

router = APIRouter()


class DayReplacementRequest(BaseModel):
    day: str
    current_recipe: str
    used_recipes: list[str] = Field(default_factory=list)


class MealPlanGenerateRequest(BaseModel):
    date: dt_date | None = None


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


@router.get("/meal-plans")
async def get_meal_plan(date: dt_date | None = None):
    meal_plan = await get_meal_plan_for_date_service(date)
    if not meal_plan:
        raise HTTPException(status_code=404, detail="Meal plan not found for requested week")

    return meal_plan


@router.post("/meal-plans/generate")
async def generate_meal_plan(payload: MealPlanGenerateRequest):
    return await generate_and_save_meal_plan_for_date_service(payload.date)
