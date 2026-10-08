from google import genai
from google.genai import types

from .config import get_settings
from .schemas import NutritionTip

settings = get_settings()


def generate_nutrition_tip_with_flash(goal: str) -> str:
    fallback = {
        "weight loss": "Build meals around vegetables, a protein source, whole grains or other high-fiber foods, and water. Aim for gradual, sustainable changes rather than extreme restriction.",
        "muscle gain": "Include a protein-rich food in each main meal, stay hydrated, and pair training with enough overall food and sleep to support recovery.",
        "general wellness": "Prioritize balanced meals with vegetables or fruit, protein, whole grains, healthy fats, and adequate water throughout the day.",
        "flexibility": "Stay hydrated and include balanced meals with protein, colorful produce, and enough overall energy to support training and recovery.",
    }.get(goal, "Stay hydrated and choose balanced meals with protein, vegetables or fruit, whole grains, and healthy fats.")

    if not settings.gemini_api_key:
        return fallback if settings.ai_fallback_enabled else "AI key is not configured."

    client = genai.Client(api_key=settings.gemini_api_key)
    prompt = f"""
Give one concise nutrition or recovery tip for a fitness user whose goal is "{goal}".
Keep it practical, general, and non-medical. Do not prescribe supplements or extreme diets.
Return JSON matching the requested schema.
"""
    response = client.models.generate_content(
        model=settings.nutrition_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=NutritionTip,
            temperature=0.4,
            max_output_tokens=300,
        ),
    )
    if getattr(response, "parsed", None):
        return NutritionTip.model_validate(response.parsed).tip
    return NutritionTip.model_validate_json(response.text).tip
