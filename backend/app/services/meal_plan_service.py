import random

import httpx

from app.config import SUPABASE_URL, SUPABASE_HEADERS, ANTHROPIC_API_KEY


async def generate_plan_service():
    async with httpx.AsyncClient() as client:
        recipes_response = await client.get(
            f"{SUPABASE_URL}/rest/v1/recipes?select=name,tags",
            headers=SUPABASE_HEADERS,
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
                "content-type": "application/json",
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
                ],
            },
        )

    data = claude_response.json()
    return data["content"][0]["text"]


async def generate_day_replacement_service(current_recipe: str, used_recipes: list[str]):
    async with httpx.AsyncClient() as client:
        recipes_response = await client.get(
            f"{SUPABASE_URL}/rest/v1/recipes?select=name",
            headers=SUPABASE_HEADERS,
        )

    recipes = recipes_response.json()
    all_recipe_names = [recipe["name"] for recipe in recipes]

    preferred_candidates = [
        name for name in all_recipe_names
        if name != current_recipe and name not in used_recipes
    ]

    if preferred_candidates:
        return random.choice(preferred_candidates)

    fallback_candidates = [name for name in all_recipe_names if name != current_recipe]
    if fallback_candidates:
        return random.choice(fallback_candidates)

    return None
