import json

from .gemini_flash_generator import generate_nutrition_tip_with_flash
from .gemini_generator import generate_workout_gemini
from .schemas import UserInput
from .updated_plan import update_workout_plan


def plan_to_json(plan) -> str:
    return plan.model_dump_json(indent=2)


def generate_plan(user: UserInput):
    workout = generate_workout_gemini(user)
    nutrition = generate_nutrition_tip_with_flash(user.goal)
    return plan_to_json(workout), nutrition


def revise_plan(original_json: str, feedback: str, goal: str, intensity: str):
    workout = update_workout_plan(original_json, feedback, goal, intensity)
    return plan_to_json(workout)
