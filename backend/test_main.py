from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
import json
import pytest
import sys
import os

# Make sure Python can find backend.app.main.py
sys.path.insert(0, os.path.dirname(__file__))

from app.main import app

client = TestClient(app)


# ── Frontend ──────────────────────────────────────────────────────

def test_frontend_includes_new_tag_input():
    response = client.get("/")
    assert response.status_code == 200
    assert 'id="new-tag-input"' in response.text


def test_frontend_includes_add_tag_button():
    response = client.get("/")
    assert response.status_code == 200
    assert "Añadir etiqueta" in response.text

def test_frontend_uses_render_backend_url_for_production():
    response = client.get("/")
    assert response.status_code == 200
    assert "https://meal-planner-igpk.onrender.com" in response.text


def test_frontend_keeps_localhost_backend_url_for_local_dev():
    response = client.get("/")
    assert response.status_code == 200
    assert "http://127.0.0.1:8000" in response.text


# ── Tags ──────────────────────────────────────────────────────────

def test_get_tags_returns_200():
    response = client.get("/tags")
    assert response.status_code == 200

def test_get_tags_returns_a_list():
    response = client.get("/tags")
    assert isinstance(response.json(), list)

def test_get_tags_includes_fish():
    response = client.get("/tags")
    assert "fish" in response.json()

# ── health ─────────────────────────────────────────────────
def test_health_returns_200():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "servicio": "planificador-comidas"}


def test_health_includes_service_name_header():
    response = client.get("/health")

    assert response.headers["X-Service-Name"] == "meal-planner"

# ── ping ────────────────────────────────────────────────

def test_ping_returns_200():
    response = client.get("/ping")
    assert response.status_code == 200


def test_ping_returns_status_ok_timestamp_and_message():
    response = client.get("/ping")
    data = response.json()

    assert data["status"] == "ok"
    assert data["message"] == "pong"
    assert "timestamp" in data

    from datetime import datetime
    datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))



# ── version ────────────────────────────────────────────────

def test_version_returns_200():
    response = client.get("/version")
    assert response.status_code == 200


def test_version_returns_expected_payload():
    response = client.get("/version")
    data = response.json()

    assert data["status"] == "ok"
    assert data["version"] == "0.1"
    assert "timestamp" in data

    from datetime import datetime
    datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))


# ── Recipes (GET) ─────────────────────────────────────────────────

def test_get_recipes_returns_200():
    mock_recipes = [
        {"id": 1, "name": "Salmon pasta", "tags": ["fish", "pasta"], "prep_minutes": 30, "recipe_ingredients": []}
    ]
    with patch("app.services.recipe_service.httpx.AsyncClient") as mock_client:
        mock_response = MagicMock()
        mock_response.json.return_value = mock_recipes
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

        response = client.get("/recipes")
        assert response.status_code == 200

def test_get_recipes_returns_a_list():
    mock_recipes = []
    with patch("app.services.recipe_service.httpx.AsyncClient") as mock_client:
        mock_response = MagicMock()
        mock_response.json.return_value = mock_recipes
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

        response = client.get("/recipes")
        assert isinstance(response.json(), list)


# ── Recipes (POST) ────────────────────────────────────────────────

def test_create_recipe_returns_success():
    new_recipe = {
        "name": "Grilled Salmon",
        "tags": ["fish"],
        "prep_minutes": 20,
        "ingredients": [{"name": "salmon fillet", "quantity": "200g"}]
    }

    with patch("app.services.recipe_service.httpx.AsyncClient") as mock_client:
        # Mock recipe insert
        mock_recipe_res = MagicMock()
        mock_recipe_res.status_code = 201
        mock_recipe_res.json.return_value = [{"id": 42}]

        # Mock ingredient upsert
        mock_ing_res = MagicMock()
        mock_ing_res.json.return_value = [{"id": 7}]

        # Mock recipe_ingredients link (no return value needed)
        mock_link_res = MagicMock()

        mock_post = AsyncMock(side_effect=[mock_recipe_res, mock_ing_res, mock_link_res])
        mock_client.return_value.__aenter__.return_value.post = mock_post

        response = client.post("/recipes", json=new_recipe)
        assert response.status_code == 200
        assert response.json()["success"] == True

def test_create_recipe_returns_recipe_id():
    new_recipe = {
        "name": "Tuna salad",
        "tags": ["fish", "salad"],
        "prep_minutes": 10,
        "ingredients": [{"name": "tuna", "quantity": "1 tin"}]
    }

    with patch("app.services.recipe_service.httpx.AsyncClient") as mock_client:
        mock_recipe_res = MagicMock()
        mock_recipe_res.status_code = 201
        mock_recipe_res.json.return_value = [{"id": 99}]

        mock_ing_res = MagicMock()
        mock_ing_res.json.return_value = [{"id": 5}]

        mock_link_res = MagicMock()

        mock_post = AsyncMock(side_effect=[mock_recipe_res, mock_ing_res, mock_link_res])
        mock_client.return_value.__aenter__.return_value.post = mock_post

        response = client.post("/recipes", json=new_recipe)
        assert "recipe_id" in response.json()

def test_create_recipe_requires_name():
    bad_recipe = {
        "tags": ["fish"],
        "ingredients": [{"name": "salmon", "quantity": "200g"}]
        # missing "name"
    }
    response = client.post("/recipes", json=bad_recipe)
    assert response.status_code == 422  # FastAPI validation error


# ── Generate Plan ─────────────────────────────────────────────────

def test_generate_plan_returns_200():
    mock_recipes = [
        {"name": "Grilled Salmon", "tags": ["fish"]},
        {"name": "Chicken pasta", "tags": ["chicken", "pasta"]},
        {"name": "Beef stew", "tags": ["beef", "comfort"]},
        {"name": "Veggie soup", "tags": ["vegetarian", "soup"]},
    ]

    mock_plan = json.dumps({
        "monday": "Chicken pasta",
        "tuesday": "Grilled Salmon",
        "wednesday": "Beef stew",
        "thursday": "Veggie soup"
    })

    with patch("app.services.meal_plan_service.httpx.AsyncClient") as mock_client:
        mock_recipes_res = MagicMock()
        mock_recipes_res.json.return_value = mock_recipes

        mock_claude_res = MagicMock()
        mock_claude_res.json.return_value = {"content": [{"text": mock_plan}]}

        mock_get = AsyncMock(return_value=mock_recipes_res)
        mock_post = AsyncMock(return_value=mock_claude_res)

        mock_client.return_value.__aenter__.return_value.get = mock_get
        mock_client.return_value.__aenter__.return_value.post = mock_post

        response = client.post("/generate-plan")
        assert response.status_code == 200

def test_generate_plan_contains_all_four_days():
    mock_recipes = [
        {"name": "Grilled Salmon", "tags": ["fish"]},
        {"name": "Chicken pasta", "tags": ["chicken"]},
        {"name": "Beef stew", "tags": ["beef"]},
        {"name": "Veggie soup", "tags": ["vegetarian"]},
    ]

    mock_plan = json.dumps({
        "monday": "Chicken pasta",
        "tuesday": "Grilled Salmon",
        "wednesday": "Beef stew",
        "thursday": "Veggie soup"
    })

    with patch("app.services.meal_plan_service.httpx.AsyncClient") as mock_client:
        mock_recipes_res = MagicMock()
        mock_recipes_res.json.return_value = mock_recipes

        mock_claude_res = MagicMock()
        mock_claude_res.json.return_value = {"content": [{"text": mock_plan}]}

        mock_get = AsyncMock(return_value=mock_recipes_res)
        mock_post = AsyncMock(return_value=mock_claude_res)

        mock_client.return_value.__aenter__.return_value.get = mock_get
        mock_client.return_value.__aenter__.return_value.post = mock_post

        response = client.post("/generate-plan")
        plan = json.loads(response.json())

        for day in ["monday", "tuesday", "wednesday", "thursday"]:
            assert day in plan, f"Missing day: {day}"


def test_generate_day_replacement_returns_200_and_recipe():
    mock_recipes = [
        {"name": "Grilled Salmon"},
        {"name": "Chicken pasta"},
        {"name": "Beef stew"},
    ]

    with patch("app.services.meal_plan_service.httpx.AsyncClient") as mock_client, \
         patch("app.services.meal_plan_service.random.choice", return_value="Beef stew"):
        mock_recipes_res = MagicMock()
        mock_recipes_res.json.return_value = mock_recipes

        mock_get = AsyncMock(return_value=mock_recipes_res)
        mock_client.return_value.__aenter__.return_value.get = mock_get

        response = client.post(
            "/generate-day-replacement",
            json={
                "day": "monday",
                "current_recipe": "Chicken pasta",
                "used_recipes": ["Grilled Salmon"],
            },
        )

        assert response.status_code == 200
        assert response.json() == {"day": "monday", "recipe": "Beef stew"}


def test_generate_day_replacement_returns_400_when_no_candidate():
    mock_recipes = [
        {"name": "Chicken pasta"},
    ]

    with patch("app.services.meal_plan_service.httpx.AsyncClient") as mock_client:
        mock_recipes_res = MagicMock()
        mock_recipes_res.json.return_value = mock_recipes

        mock_get = AsyncMock(return_value=mock_recipes_res)
        mock_client.return_value.__aenter__.return_value.get = mock_get

        response = client.post(
            "/generate-day-replacement",
            json={
                "day": "wednesday",
                "current_recipe": "Chicken pasta",
                "used_recipes": [],
            },
        )

        assert response.status_code == 400
        assert response.json()["detail"] == "No replacement recipe available"

# ── Recipes (DELETE) ────────────────────────────────────────────────

def test_delete_recipe_returns_success():
    with patch("app.services.recipe_service.httpx.AsyncClient") as mock_client:
        mock_api = mock_client.return_value.__aenter__.return_value

        mock_delete_res_links = MagicMock()
        mock_delete_res_links.status_code = 204

        mock_delete_res_recipe = MagicMock()
        mock_delete_res_recipe.status_code = 200
        mock_delete_res_recipe.json.return_value = [{"id": 42}]

        mock_api.delete = AsyncMock(
            side_effect=[mock_delete_res_links, mock_delete_res_recipe]
        )

        response = client.delete("/recipes/42")

        assert response.status_code == 200
        assert response.json() == {"success": True}


def test_delete_nonexistent_recipe_returns_404():
    with patch("app.services.recipe_service.httpx.AsyncClient") as mock_client:
        mock_api = mock_client.return_value.__aenter__.return_value

        mock_delete_res_links = MagicMock()
        mock_delete_res_links.status_code = 204

        mock_delete_res_recipe = MagicMock()
        mock_delete_res_recipe.status_code = 200
        mock_delete_res_recipe.json.return_value = []

        mock_api.delete = AsyncMock(
            side_effect=[mock_delete_res_links, mock_delete_res_recipe]
        )

        response = client.delete("/recipes/999")

        assert response.status_code == 404
        assert response.json()["detail"] == "Recipe not found"


def test_delete_recipe_deletes_links_before_recipe():
    with patch("app.services.recipe_service.httpx.AsyncClient") as mock_client:
        mock_api = mock_client.return_value.__aenter__.return_value

        mock_delete_res_links = MagicMock()
        mock_delete_res_links.status_code = 204

        mock_delete_res_recipe = MagicMock()
        mock_delete_res_recipe.status_code = 200
        mock_delete_res_recipe.json.return_value = [{"id": 42}]

        mock_api.delete = AsyncMock(
            side_effect=[mock_delete_res_links, mock_delete_res_recipe]
        )

        response = client.delete("/recipes/42")

        assert response.status_code == 200
        assert mock_api.delete.await_count == 2

        first_delete_url = mock_api.delete.await_args_list[0].args[0]
        second_delete_url = mock_api.delete.await_args_list[1].args[0]

        assert "recipe_ingredients?recipe_id=eq.42" in first_delete_url
        assert "recipes?id=eq.42" in second_delete_url

# ── Weekly Meal Plans ────────────────────────────────────────────────

def test_get_week_start_sunday():
    from datetime import date
    from app.services.meal_plan_service import get_week_start

    assert get_week_start(date(2026, 4, 1), "sunday") == date(2026, 3, 29)


def test_get_week_start_monday():
    from datetime import date
    from app.services.meal_plan_service import get_week_start

    assert get_week_start(date(2026, 4, 1), "monday") == date(2026, 3, 30)


def test_get_week_start_when_date_is_start_day():
    from datetime import date
    from app.services.meal_plan_service import get_week_start

    assert get_week_start(date(2026, 3, 29), "sunday") == date(2026, 3, 29)


def test_get_meal_plan_for_existing_week_returns_200():
    saved_plan = {
        "week_start_date": "2026-03-29",
        "monday": "Chicken pasta",
        "tuesday": "Grilled Salmon",
        "wednesday": "Beef stew",
        "thursday": "Veggie soup",
    }

    with patch("app.services.meal_plan_service.WEEK_START_DAY", "sunday"), \
         patch("app.services.meal_plan_service.httpx.AsyncClient") as mock_client:
        mock_response = MagicMock()
        mock_response.json.return_value = [saved_plan]
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

        response = client.get("/meal-plans?date=2026-04-01")

        assert response.status_code == 200
        assert response.json()["week_start_date"] == "2026-03-29"


def test_get_meal_plan_for_missing_week_returns_404():
    with patch("app.services.meal_plan_service.WEEK_START_DAY", "sunday"), \
         patch("app.services.meal_plan_service.httpx.AsyncClient") as mock_client:
        mock_response = MagicMock()
        mock_response.json.return_value = []
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

        response = client.get("/meal-plans?date=2026-04-01")

        assert response.status_code == 404
        assert response.json()["detail"] == "Meal plan not found for requested week"


def test_generate_meal_plan_creates_plan_for_week():
    generated_plan = json.dumps({
        "monday": "Chicken pasta",
        "tuesday": "Grilled Salmon",
        "wednesday": "Beef stew",
        "thursday": "Veggie soup",
    })

    saved_plan = [{
        "week_start_date": "2026-03-29",
        "monday": "Chicken pasta",
        "tuesday": "Grilled Salmon",
        "wednesday": "Beef stew",
        "thursday": "Veggie soup",
    }]

    with patch("app.services.meal_plan_service.WEEK_START_DAY", "sunday"), \
         patch("app.services.meal_plan_service.generate_plan_service", AsyncMock(return_value=generated_plan)), \
         patch("app.services.meal_plan_service.httpx.AsyncClient") as mock_client:
        mock_response = MagicMock()
        mock_response.json.return_value = saved_plan
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)

        response = client.post("/meal-plans/generate", json={"date": "2026-04-01"})

        assert response.status_code == 200
        assert response.json()["week_start_date"] == "2026-03-29"


def test_generate_meal_plan_overwrites_existing_week_plan():
    first_generated_plan = json.dumps({
        "monday": "Recipe A",
        "tuesday": "Recipe B",
        "wednesday": "Recipe C",
        "thursday": "Recipe D",
    })

    overwritten_plan = [{
        "week_start_date": "2026-03-29",
        "monday": "Recipe A",
        "tuesday": "Recipe B",
        "wednesday": "Recipe C",
        "thursday": "Recipe D",
    }]

    with patch("app.services.meal_plan_service.WEEK_START_DAY", "sunday"), \
         patch("app.services.meal_plan_service.generate_plan_service", AsyncMock(return_value=first_generated_plan)), \
         patch("app.services.meal_plan_service.httpx.AsyncClient") as mock_client:
        mock_response = MagicMock()
        mock_response.json.return_value = overwritten_plan
        mock_post = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value.post = mock_post

        response = client.post("/meal-plans/generate", json={"date": "2026-04-01"})

        assert response.status_code == 200
        assert response.json()["monday"] == "Recipe A"
        post_url = mock_post.await_args.args[0]
        assert "on_conflict=week_start_date" in post_url
