from fastapi import APIRouter

from app.models import RecipeCreate
from app.services.recipe_service import (
    create_recipe_service,
    delete_recipe_service,
    get_all_recipes,
    get_recipe_by_id,
    update_recipe_service,
)

router = APIRouter()

@router.get("/recipes")
async def get_recipes():
    return await get_all_recipes()

@router.get("/recipes/{recipe_id}")
async def get_recipe(recipe_id: int):
    return await get_recipe_by_id(recipe_id)

@router.post("/recipes")
async def create_recipe(recipe: RecipeCreate):
    return await create_recipe_service(recipe)

@router.put("/recipes/{recipe_id}")
async def update_recipe(recipe_id: int, recipe: RecipeCreate):
    return await update_recipe_service(recipe_id, recipe)

@router.delete("/recipes/{recipe_id}")
async def delete_recipe(recipe_id: int):
    return await delete_recipe_service(recipe_id)