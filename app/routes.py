import json
from pathlib import Path

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from .config import get_settings
from .database import delete_user, get_all_users_with_plans, get_plan, get_user, save_plan, save_user, update_plan
from .schemas import FeedbackRequest, UserInput
from .services import generate_plan, revise_plan

router = APIRouter()
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")
settings = get_settings()


def _render_result(request: Request, user, plan, message=None):
    parsed_plan = json.loads(plan.original_plan if not plan.updated_plan else plan.updated_plan)
    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={
            "user": user,
            "plan": parsed_plan,
            "nutrition_tip": plan.nutrition_tip,
            "feedback": plan.feedback,
            "message": message,
            "is_updated": bool(plan.updated_plan),
        },
    )


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={})


@router.post("/generate-workout", response_class=HTMLResponse)
def generate_workout(
    request: Request,
    username: str = Form(...),
    user_id: str = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),
):
    try:
        data = UserInput(
            username=username,
            user_id=user_id,
            age=age,
            weight=weight,
            goal=goal,
            intensity=intensity,
        )
        save_user(data)
        original_plan, nutrition_tip = generate_plan(data)
        plan = save_plan(data.user_id, original_plan, nutrition_tip)
        user = get_user(data.user_id)
        return _render_result(request, user, plan)
    except Exception as exc:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={"error": str(exc)},
            status_code=400,
        )


@router.post("/submit-feedback", response_class=HTMLResponse)
def submit_feedback(
    request: Request,
    user_id: str = Form(...),
    feedback: str = Form(...),
):
    try:
        req = FeedbackRequest(user_id=user_id, feedback=feedback)
        user = get_user(req.user_id)
        plan = get_plan(req.user_id)
        if not user or not plan:
            raise ValueError("User or workout plan not found. Generate a plan first.")

        updated_json = revise_plan(plan.original_plan, req.feedback, user.goal, user.intensity)
        update_plan(req.user_id, updated_json, req.feedback, plan.nutrition_tip)
        refreshed = get_plan(req.user_id)
        return _render_result(
            request,
            user,
            refreshed,
            message="Your workout plan has been updated successfully.",
        )
    except Exception as exc:
        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={"error": str(exc), "user_id": user_id},
            status_code=400,
        )


@router.get("/view-all-users", response_class=HTMLResponse)
def view_all_users(request: Request, admin_token: str | None = None):
    if settings.admin_token and admin_token != settings.admin_token:
        return templates.TemplateResponse(
            request=request,
            name="admin_login.html",
            context={"error": None},
            status_code=401,
        )
    rows = get_all_users_with_plans()
    return templates.TemplateResponse(
        request=request,
        name="all_users.html",
        context={"rows": rows, "admin_token": admin_token},
    )


@router.post("/admin/delete-user")
def admin_delete_user(user_id: str = Form(...), admin_token: str = Form(...)):
    if admin_token != settings.admin_token:
        raise HTTPException(status_code=403, detail="Invalid admin token.")
    delete_user(user_id)
    return RedirectResponse(url=f"/view-all-users?admin_token={admin_token}", status_code=303)


# JSON API endpoints
@router.get("/api/health")
def health():
    return {"status": "ok", "service": "FitBuddy"}


@router.post("/api/generate-workout")
def api_generate_workout(data: UserInput):
    save_user(data)
    original_plan, nutrition_tip = generate_plan(data)
    save_plan(data.user_id, original_plan, nutrition_tip)
    return {
        "user": data.model_dump(),
        "workout_plan": json.loads(original_plan),
        "nutrition_tip": nutrition_tip,
    }


@router.post("/api/submit-feedback")
def api_submit_feedback(data: FeedbackRequest):
    user = get_user(data.user_id)
    plan = get_plan(data.user_id)
    if not user or not plan:
        raise HTTPException(status_code=404, detail="User or plan not found.")

    updated_json = revise_plan(plan.original_plan, data.feedback, user.goal, user.intensity)
    update_plan(data.user_id, updated_json, data.feedback, plan.nutrition_tip)
    return {
        "user_id": data.user_id,
        "updated_plan": json.loads(updated_json),
        "nutrition_tip": plan.nutrition_tip,
        "feedback": data.feedback,
    }


@router.get("/api/users")
def api_users(admin_token: str):
    if admin_token != settings.admin_token:
        raise HTTPException(status_code=403, detail="Invalid admin token.")
    rows = get_all_users_with_plans()
    return [
        {
            "user": {
                "id": user.id,
                "user_id": user.user_id,
                "username": user.username,
                "age": user.age,
                "weight": user.weight,
                "goal": user.goal,
                "intensity": user.intensity,
            },
            "plan": None if not plan else {
                "original_plan": json.loads(plan.original_plan),
                "updated_plan": json.loads(plan.updated_plan) if plan.updated_plan else None,
                "nutrition_tip": plan.nutrition_tip,
                "feedback": plan.feedback,
            },
        }
        for user, plan in rows
    ]
