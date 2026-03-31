import json
import random
from datetime import UTC, date, datetime

import httpx

from app.config import SUPABASE_URL, SUPABASE_HEADERS, ANTHROPIC_API_KEY, WEEK_START_DAY


WEEKDAY_MAP = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}


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


def get_week_start(target_date: date, week_start_day: str) -> date:
    week_start_day_normalized = week_start_day.lower()
    if week_start_day_normalized not in WEEKDAY_MAP:
        raise ValueError(f"Unsupported week_start_day: {week_start_day}")

    start_weekday = WEEKDAY_MAP[week_start_day_normalized]
    days_since_start = (target_date.weekday() - start_weekday) % 7
    return target_date.fromordinal(target_date.toordinal() - days_since_start)


async def get_meal_plan_for_date_service(target_date: date | None = None):
    date_to_use = target_date or datetime.now(UTC).date()
    week_start_date = get_week_start(date_to_use, WEEK_START_DAY)

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{SUPABASE_URL}/rest/v1/meal_plans?week_start_date=eq.{week_start_date.isoformat()}&select=*",
            headers=SUPABASE_HEADERS,
        )

    records = response.json()
    if not records:
        return None

    return records[0]


async def generate_and_save_meal_plan_for_date_service(target_date: date | None = None):
    date_to_use = target_date or datetime.now(UTC).date()
    week_start_date = get_week_start(date_to_use, WEEK_START_DAY)

    generated_plan_json = await generate_plan_service()
    generated_plan = json.loads(generated_plan_json)

    payload = {
        "week_start_date": week_start_date.isoformat(),
        "monday": generated_plan.get("monday"),
        "tuesday": generated_plan.get("tuesday"),
        "wednesday": generated_plan.get("wednesday"),
        "thursday": generated_plan.get("thursday"),
    }

    headers = {
        **SUPABASE_HEADERS,
        "Prefer": "resolution=merge-duplicates,return=representation",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SUPABASE_URL}/rest/v1/meal_plans?on_conflict=week_start_date",
            headers=headers,
            json=payload,
        )

    saved_records = response.json()
    if saved_records:
        return saved_records[0]

    return payload
