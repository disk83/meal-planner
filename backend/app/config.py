import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

SUPABASE_HEADERS = {
    "apikey": SUPABASE_ANON_KEY,
    "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
    "Content-Type": "application/json",
}

BASE_DIR = Path(__file__).resolve().parent.parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

AVAILABLE_TAGS = [
    "fish", "chicken", "beef", "pork", "vegetarian", "vegan",
    "pasta", "soup", "salad", "quick", "comfort", "spicy"
]