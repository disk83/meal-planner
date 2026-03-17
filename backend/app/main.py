from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import FRONTEND_DIR
from app.routers import frontend, health, meal_plan, recipes, tags

app = FastAPI()

app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(frontend.router)
app.include_router(health.router)
app.include_router(tags.router)
app.include_router(recipes.router)
app.include_router(meal_plan.router)
