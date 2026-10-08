import os
os.environ["AI_FALLBACK_ENABLED"] = "true"
os.environ["GEMINI_API_KEY"] = ""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert "FitBuddy" in response.text


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_generate_api_without_gemini():
    payload = {
        "username": "Test User",
        "user_id": "TEST001",
        "age": 20,
        "weight": 60,
        "goal": "general wellness",
        "intensity": "medium",
    }
    response = client.post("/api/generate-workout", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert len(body["workout_plan"]["days"]) == 7
    assert body["nutrition_tip"]


def test_feedback_api_without_gemini():
    payload = {"user_id": "TEST001", "feedback": "Add more cardio"}
    response = client.post("/api/submit-feedback", json=payload)
    assert response.status_code == 200
    assert len(response.json()["updated_plan"]["days"]) == 7
