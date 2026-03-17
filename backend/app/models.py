from pydantic import BaseModel

class Ingredient(BaseModel):
    name: str
    quantity: str

class RecipeCreate(BaseModel):
    name: str
    tags: list[str]
    prep_minutes: int | None = None
    ingredients: list[Ingredient]