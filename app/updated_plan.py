from google import genai
from google.genai import types

from .config import get_settings
from .schemas import WorkoutPlan

settings = get_settings()


def update_workout_plan(original_plan: str, feedback: str, goal: str, intensity: str) -> WorkoutPlan:
    if not settings.gemini_api_key:
        # Local fallback: keep a valid plan and make the feedback visible as a note.
        plan = WorkoutPlan.model_validate_json(original_plan)
        plan.days[0].cooldown = f"Updated from feedback: {feedback}. " + plan.days[0].cooldown
        return plan

    client = genai.Client(api_key=settings.gemini_api_key)
    prompt = f"""
Update the existing 7-day workout plan according to the user's feedback.

Goal: {goal}
Intensity: {intensity}
User feedback: {feedback}

Original plan:
{original_plan}

Rules:
- Preserve exactly 7 days.
- Apply the feedback where reasonable.
- Keep the plan practical and safe.
- Do not diagnose or prescribe medical treatment.
- Return only the structured workout plan.
"""
    response = client.models.generate_content(
        model=settings.workout_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=WorkoutPlan,
            temperature=0.5,
            max_output_tokens=5000,
        ),
    )
    if getattr(response, "parsed", None):
        return WorkoutPlan.model_validate(response.parsed)
    return WorkoutPlan.model_validate_json(response.text)
