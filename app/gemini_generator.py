from google import genai
from google.genai import types

from .config import get_settings
from .schemas import UserInput, WorkoutPlan

settings = get_settings()


def _client():
    if not settings.gemini_api_key:
        return None
    return genai.Client(api_key=settings.gemini_api_key)


def _fallback_plan(user: UserInput) -> WorkoutPlan:
    focus = {
        "weight loss": ["Full body + cardio", "Cardio", "Lower body", "Active recovery", "Upper body", "Intervals", "Mobility + light cardio"],
        "muscle gain": ["Full body", "Upper body", "Lower body", "Recovery", "Push", "Pull", "Legs + core"],
        "general wellness": ["Full body", "Cardio", "Upper body", "Mobility", "Lower body", "Light cardio", "Full body"],
        "flexibility": ["Full-body mobility", "Hips + hamstrings", "Upper-body mobility", "Yoga", "Spine + core", "Lower-body mobility", "Gentle full body"],
    }[user.goal]

    exercises = [
        ["Bodyweight squat", "3 x 10", "60 sec", "Controlled tempo"],
        ["Incline push-up", "3 x 8", "60 sec", "Keep core braced"],
        ["Glute bridge", "3 x 12", "45 sec", "Pause at the top"],
        ["Bird dog", "3 x 10/side", "45 sec", "Move slowly"],
    ]
    days = []
    for i, f in enumerate(focus, 1):
        days.append({
            "day": f"Day {i}",
            "focus": f,
            "warm_up": "5–10 minutes of easy walking and dynamic mobility.",
            "exercises": [
                {"name": name, "sets_reps": reps, "rest": rest, "notes": notes}
                for name, reps, rest, notes in exercises
            ],
            "cooldown": "5–10 minutes of gentle stretching and relaxed breathing.",
        })
    return WorkoutPlan(days=days)


def generate_workout_gemini(user: UserInput) -> WorkoutPlan:
    client = _client()
    if not client:
        if settings.ai_fallback_enabled:
            return _fallback_plan(user)
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    prompt = f"""
Create a safe, practical 7-day beginner-to-intermediate fitness plan.

User:
- Name: {user.username}
- Age: {user.age}
- Weight: {user.weight} kg
- Goal: {user.goal}
- Preferred intensity: {user.intensity}

Requirements:
- Exactly 7 days.
- Each day must have a focus, warm-up, 3–5 exercises, and cooldown/recovery.
- Include exercise name, sets/reps or duration, rest, and a short technique note.
- Adjust difficulty to the selected intensity.
- Include at least one lighter/recovery day where appropriate.
- Do not prescribe medication or diagnose conditions.
- Avoid extreme calorie restriction.
- Return only the requested structured data.
"""

    response = client.models.generate_content(
        model=settings.workout_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=WorkoutPlan,
            temperature=0.6,
            max_output_tokens=5000,
        ),
    )
    if getattr(response, "parsed", None):
        return WorkoutPlan.model_validate(response.parsed)
    return WorkoutPlan.model_validate_json(response.text)
