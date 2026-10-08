from typing import Literal

from pydantic import BaseModel, Field, field_validator


Goal = Literal["weight loss", "muscle gain", "general wellness", "flexibility"]
Intensity = Literal["low", "medium", "high"]


class UserInput(BaseModel):
    username: str = Field(min_length=2, max_length=80)
    user_id: str = Field(min_length=2, max_length=40, pattern=r"^[A-Za-z0-9_-]+$")
    age: int = Field(ge=13, le=100)
    weight: float = Field(gt=20, le=400)
    goal: Goal
    intensity: Intensity

    @field_validator("username")
    @classmethod
    def clean_name(cls, value: str) -> str:
        return " ".join(value.strip().split())


class FeedbackRequest(BaseModel):
    user_id: str = Field(min_length=2, max_length=40)
    feedback: str = Field(min_length=5, max_length=1000)


class WorkoutExercise(BaseModel):
    name: str
    sets_reps: str
    rest: str
    notes: str


class WorkoutDay(BaseModel):
    day: str
    focus: str
    warm_up: str
    exercises: list[WorkoutExercise]
    cooldown: str


class WorkoutPlan(BaseModel):
    days: list[WorkoutDay] = Field(min_length=7, max_length=7)


class NutritionTip(BaseModel):
    tip: str
