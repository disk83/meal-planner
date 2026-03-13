from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException
from dotenv import load_dotenv
from pydantic import BaseModel
import httpx
import os
from pathlib import Path

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

SUPABASE_HEADERS = {
    "apikey": SUPABASE_ANON_KEY,
    "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
    "Content-Type": "application/json"
}

BASE_DIR = Path(__file__).resolve().parent.parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

app = FastAPI()
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

@app.get("/")
async def serve_frontend():
    return FileResponse(str(FRONTEND_DIR / "index.html"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

AVAILABLE_TAGS = [
    "fish", "chicken", "beef", "pork", "vegetarian", "vegan",
    "pasta", "soup", "salad", "quick", "comfort", "spicy", "beef"
]

@app.get("/tags")
async def get_tags():
    return AVAILABLE_TAGS

# ── Models ────────────────────────────────────────────────────────
class Ingredient(BaseModel):
    name: str
    quantity: str

class RecipeCreate(BaseModel):
    name: str
    tags: list[str]
    prep_minutes: int | None = None
    ingredients: list[Ingredient]

# ── Route 1: fetch all recipes ────────────────────────────────────
@app.get("/recipes")
async def get_recipes():
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{SUPABASE_URL}/rest/v1/recipes?select=id,name,tags,prep_minutes,recipe_ingredients(quantity,ingredients(name))",
            headers=SUPABASE_HEADERS
        )
    return response.json()

# ── Route 2: add a recipe with ingredients ────────────────────────
async def get_or_create_ingredient(client: httpx.AsyncClient, name: str) -> int:
    clean_name = name.lower().strip()

    # Try to insert (upsert)
    ing_res = await client.post(
        f"{SUPABASE_URL}/rest/v1/ingredients",
        headers={**SUPABASE_HEADERS, "Prefer": "return=representation,resolution=merge-duplicates"},
        json={"name": clean_name}
    )
    data = ing_res.json()

    # If upsert returned the row, use it
    if data and isinstance(data, list) and len(data) > 0:
        return data[0]["id"]

    # Otherwise fetch the existing row by name
    fetch_res = await client.get(
        f"{SUPABASE_URL}/rest/v1/ingredients?name=eq.{clean_name}&select=id",
        headers=SUPABASE_HEADERS
    )
    return fetch_res.json()[0]["id"]

@app.post("/recipes")
async def create_recipe(recipe: RecipeCreate):
    async with httpx.AsyncClient() as client:

        # 1. Insert the recipe
        recipe_res = await client.post(
            f"{SUPABASE_URL}/rest/v1/recipes",
            headers={
                **SUPABASE_HEADERS,
                "Prefer": "return=representation",
                "Resolution": "merge-duplicates"
            },
            json={
                "name": recipe.name,
                "tags": recipe.tags,
                "prep_minutes": recipe.prep_minutes
            }
        )
        if recipe_res.status_code != 201:
            raise HTTPException(status_code=500, detail="Failed to create recipe")

        recipe_id = recipe_res.json()[0]["id"]

        # 2. For each ingredient: upsert into ingredients table, then link
        for ing in recipe.ingredients:
            # Upsert ingredient by name (reuse if already exists)
            ingredient_id = await get_or_create_ingredient(client, ing.name)

            # Link ingredient to recipe
            await client.post(
                f"{SUPABASE_URL}/rest/v1/recipe_ingredients",
                headers=SUPABASE_HEADERS,
                json={
                    "recipe_id": recipe_id,
                    "ingredient_id": ingredient_id,
                    "quantity": ing.quantity
                }
            )

    return {"success": True, "recipe_id": recipe_id}

# ── Route: get a single recipe with ingredients ───────────────────
@app.get("/recipes/{recipe_id}")
async def get_recipe(recipe_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{SUPABASE_URL}/rest/v1/recipes?id=eq.{recipe_id}&select=id,name,tags,prep_minutes,recipe_ingredients(quantity,ingredients(name))",
            headers=SUPABASE_HEADERS
        )
    data = response.json()
    if not data:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return data[0]


# ── Route: update a recipe ────────────────────────────────────────
@app.put("/recipes/{recipe_id}")
async def update_recipe(recipe_id: int, recipe: RecipeCreate):
    async with httpx.AsyncClient() as client:

        # 1. Update the recipe row
        await client.patch(
            f"{SUPABASE_URL}/rest/v1/recipes?id=eq.{recipe_id}",
            headers={
                **SUPABASE_HEADERS,
                "Prefer": "return=representation",
                "Resolution": "merge-duplicates"
            },
            json={
                "name": recipe.name,
                "tags": recipe.tags,
                "prep_minutes": recipe.prep_minutes
            }
        )

        # 2. Delete existing ingredient links
        await client.delete(
            f"{SUPABASE_URL}/rest/v1/recipe_ingredients?recipe_id=eq.{recipe_id}",
            headers=SUPABASE_HEADERS
        )

        # 3. Re-insert ingredients (same logic as create)
        for ing in recipe.ingredients:
            ingredient_id = await get_or_create_ingredient(client, ing.name)

            await client.post(
                f"{SUPABASE_URL}/rest/v1/recipe_ingredients",
                headers=SUPABASE_HEADERS,
                json={
                    "recipe_id": recipe_id,
                    "ingredient_id": ingredient_id,
                    "quantity": ing.quantity
                }
            )

    return {"success": True, "recipe_id": recipe_id}

# ── Route: delete a recipe ────────────────────────────────────────
@app.delete("/recipes/{recipe_id}")
async def delete_recipe(recipe_id: int):
    async with httpx.AsyncClient() as client:

        # 1. Delete ingredient links
        ingredients_res = await client.delete(
            f"{SUPABASE_URL}/rest/v1/recipe_ingredients?recipe_id=eq.{recipe_id}",
            headers=SUPABASE_HEADERS
        )

        if ingredients_res.status_code not in [200, 204]:
            raise HTTPException(
                status_code=500,
                detail="Failed to delete recipe ingredients"
            )

        # 2. Delete the recipe itself, returning deleted row(s)
        recipe_delete_headers = {
            **SUPABASE_HEADERS,
            "Prefer": "return=representation"
        }

        recipe_res = await client.delete(
            f"{SUPABASE_URL}/rest/v1/recipes?id=eq.{recipe_id}",
            headers=recipe_delete_headers
        )

        if recipe_res.status_code not in [200, 204]:
            raise HTTPException(status_code=500, detail="Failed to delete recipe")

        deleted_recipes = recipe_res.json() if recipe_res.status_code == 200 else []

        if not deleted_recipes:
            raise HTTPException(status_code=404, detail="Recipe not found")

    return {"success": True}


# ── Route 3: generate a meal plan using Claude ────────────────────
@app.post("/generate-plan")
async def generate_plan():
    async with httpx.AsyncClient() as client:
        recipes_response = await client.get(
            f"{SUPABASE_URL}/rest/v1/recipes?select=name,tags",
            headers=SUPABASE_HEADERS
        )
    recipes = recipes_response.json()

    recipe_list = "\n".join([
        f"{i+1}. {r['name']} (tags: {', '.join(r['tags']) if r['tags'] else 'none'})"
        for i, r in enumerate(recipes)
    ])

    async with httpx.AsyncClient() as client:
        claude_response = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 500,
                "temperature": 0.9,
                "system": "You are a meal planning assistant. You suggest dinners for Monday to Thursday based on available recipes and constraints. You always respond with valid JSON and nothing else — no explanation, no markdown.",
                "messages": [
                    {
                        "role": "user",
                        "content": f"""Here are the available recipes (numbered):
{recipe_list}

Instructions:
- Pick 4 different recipes for the week
- Use a random starting point each time — do not always start from the top of the list
- Tuesday must be a fish dish (tags include 'fish')
- Vary the types of meals across the week

Respond with exactly this JSON format:
{{
  "monday": "recipe name",
  "tuesday": "recipe name",
  "wednesday": "recipe name",
  "thursday": "recipe name"
}}"""
                    }
                ]
            }
        )

    data = claude_response.json()
    meal_plan_text = data["content"][0]["text"]
    return meal_plan_text