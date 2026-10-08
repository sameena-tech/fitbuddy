import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()


class Settings(BaseModel):
    app_name: str = "FitBuddy"
    database_url: str = Field(default="sqlite:///./fitbuddy.db")
    gemini_api_key: str | None = None
    workout_model: str = "gemini-3.8-flash"
    nutrition_model: str = "gemini-3.8-flash"
    admin_token: str = "fitbuddy-admin"
    ai_fallback_enabled: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings(
        database_url=os.getenv("DATABASE_URL", "sqlite:///./fitbuddy.db"),
        gemini_api_key=os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"),
        workout_model=os.getenv("GEMINI_WORKOUT_MODEL", "gemini-3.8-flash"),
        nutrition_model=os.getenv("GEMINI_NUTRITION_MODEL", "gemini-3.8-flash"),
        admin_token=os.getenv("ADMIN_TOKEN", "fitbuddy-admin"),
        ai_fallback_enabled=os.getenv("AI_FALLBACK_ENABLED", "true").lower() == "true",
    )
