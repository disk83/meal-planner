import httpx
from fastapi import HTTPException

from app.config import SUPABASE_URL, SUPABASE_HEADERS
from app.models import RecipeCreate


async def get_all_recipes():
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{SUPABASE_URL}/rest/v1/recipes?select=id,name,tags,prep_minutes,recipe_ingredients(quantity,ingredients(name))",
            headers=SUPABASE_HEADERS,
        )
    return response.json()


async def get_recipe_by_id(recipe_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{SUPABASE_URL}/rest/v1/recipes?id=eq.{recipe_id}&select=id,name,tags,prep_minutes,recipe_ingredients(quantity,ingredients(name))",
            headers=SUPABASE_HEADERS,
        )
    data = response.json()
    if not data:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return data[0]


async def get_or_create_ingredient(client: httpx.AsyncClient, name: str) -> int:
    clean_name = name.lower().strip()

    ing_res = await client.post(
        f"{SUPABASE_URL}/rest/v1/ingredients",
        headers={**SUPABASE_HEADERS, "Prefer": "return=representation,resolution=merge-duplicates"},
        json={"name": clean_name},
    )
    data = ing_res.json()

    if data and isinstance(data, list) and len(data) > 0:
        return data[0]["id"]

    fetch_res = await client.get(
        f"{SUPABASE_URL}/rest/v1/ingredients?name=eq.{clean_name}&select=id",
        headers=SUPABASE_HEADERS,
    )
    return fetch_res.json()[0]["id"]


async def create_recipe_service(recipe: RecipeCreate):
    async with httpx.AsyncClient() as client:
        recipe_res = await client.post(
            f"{SUPABASE_URL}/rest/v1/recipes",
            headers={
                **SUPABASE_HEADERS,
                "Prefer": "return=representation",
                "Resolution": "merge-duplicates",
            },
            json={
                "name": recipe.name,
                "tags": recipe.tags,
                "prep_minutes": recipe.prep_minutes,
            },
        )

        if recipe_res.status_code != 201:
            raise HTTPException(status_code=500, detail="Failed to create recipe")

        recipe_id = recipe_res.json()[0]["id"]

        for ing in recipe.ingredients:
            ingredient_id = await get_or_create_ingredient(client, ing.name)

            await client.post(
                f"{SUPABASE_URL}/rest/v1/recipe_ingredients",
                headers=SUPABASE_HEADERS,
                json={
                    "recipe_id": recipe_id,
                    "ingredient_id": ingredient_id,
                    "quantity": ing.quantity,
                },
            )

    return {"success": True, "recipe_id": recipe_id}


async def update_recipe_service(recipe_id: int, recipe: RecipeCreate):
    async with httpx.AsyncClient() as client:
        await client.patch(
            f"{SUPABASE_URL}/rest/v1/recipes?id=eq.{recipe_id}",
            headers={
                **SUPABASE_HEADERS,
                "Prefer": "return=representation",
                "Resolution": "merge-duplicates",
            },
            json={
                "name": recipe.name,
                "tags": recipe.tags,
                "prep_minutes": recipe.prep_minutes,
            },
        )

        await client.delete(
            f"{SUPABASE_URL}/rest/v1/recipe_ingredients?recipe_id=eq.{recipe_id}",
            headers=SUPABASE_HEADERS,
        )

        for ing in recipe.ingredients:
            ingredient_id = await get_or_create_ingredient(client, ing.name)

            await client.post(
                f"{SUPABASE_URL}/rest/v1/recipe_ingredients",
                headers=SUPABASE_HEADERS,
                json={
                    "recipe_id": recipe_id,
                    "ingredient_id": ingredient_id,
                    "quantity": ing.quantity,
                },
            )

    return {"success": True, "recipe_id": recipe_id}


async def delete_recipe_service(recipe_id: int):
    async with httpx.AsyncClient() as client:
        ingredients_res = await client.delete(
            f"{SUPABASE_URL}/rest/v1/recipe_ingredients?recipe_id=eq.{recipe_id}",
            headers=SUPABASE_HEADERS,
        )

        if ingredients_res.status_code not in [200, 204]:
            raise HTTPException(
                status_code=500,
                detail="Failed to delete recipe ingredients",
            )

        recipe_delete_headers = {
            **SUPABASE_HEADERS,
            "Prefer": "return=representation",
        }

        recipe_res = await client.delete(
            f"{SUPABASE_URL}/rest/v1/recipes?id=eq.{recipe_id}",
            headers=recipe_delete_headers,
        )

        if recipe_res.status_code not in [200, 204]:
            raise HTTPException(status_code=500, detail="Failed to delete recipe")

        deleted_recipes = recipe_res.json() if recipe_res.status_code == 200 else []

        if not deleted_recipes:
            raise HTTPException(status_code=404, detail="Recipe not found")

    return {"success": True}