# AGENTS.md

## Project purpose
This is a learning project to build an AI-assisted meal planner web app.

The app currently:
- uses a FastAPI backend
- uses a simple HTML frontend
- stores recipe data in Supabase
- calls Claude to generate a weekly meal plan
- supports adding and editing recipes
- is still MVP-level and intentionally simple

## Main development goal
The main goal is learning AI-assisted software development step by step.

This is not a production system yet.
Prioritize clarity, small changes, and preserving working behavior.

## Current structure
- `backend/main.py` contains the main FastAPI backend logic
- `backend/test_main.py` contains early test code
- `frontend/index.html` contains the frontend
- `requirements.txt` contains Python dependencies
- `.env` is local only and must never be committed

## Rules for making changes
1. Prefer small, incremental changes
2. Do not refactor large parts of the project unless explicitly asked
3. Preserve current working MVP behavior
4. Explain proposed changes clearly
5. Keep solutions simple and beginner-friendly
6. Do not introduce unnecessary frameworks or abstractions
7. Never commit secrets or API keys
8. Prefer changes that help learning and understanding

## Coding guidelines
- Keep the current FastAPI + simple frontend structure unless asked otherwise
- Keep backend changes minimal and readable
- Reuse existing patterns in `main.py` where reasonable
- When adding a feature, avoid changing unrelated code
- If a feature needs both backend and frontend work, keep each change small and clearly scoped

## Testing
- If possible, propose or add a simple test for the changed behavior
- Do not invent a large test framework unless explicitly asked
- Prefer lightweight validation suitable for an MVP

## Preferred workflow
When working on a change:
1. read the relevant files
2. make the smallest useful change
3. review the change for simplicity and safety
4. run available tests if practical
5. prepare the change for review in a PR

## Current likely priorities
- add recipe deletion
- improve ingredient management
- improve meal generation logic
- gradually improve structure without large rewrites