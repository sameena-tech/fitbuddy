# FitBuddy – AI Fitness Plan Generator

FitBuddy is a FastAPI + Jinja2 + SQLite web application that generates personalized 7-day workout plans and nutrition/recovery tips with Google's Gemini API.

## Architecture

- Frontend: HTML + Jinja2 + responsive CSS
- Backend: FastAPI
- AI: Google Gemini via the current `google-genai` SDK
- Database: SQLite + SQLAlchemy
- API: REST endpoints under `/api`
- Admin: token-protected dashboard at `/view-all-users`

The original documentation describes Gemini 1.5 Pro and Gemini Flash. Those model names are not used here because the current Gemini API model catalog has moved on. The project defaults to the currently documented `gemini-3.8-flash` model and keeps the model names configurable through `.env`.

## Features

1. Collects name, user ID, age, weight, goal, and workout intensity.
2. Generates exactly seven workout days.
3. Generates a concise nutrition/recovery tip.
4. Saves users and both original/updated plans in SQLite.
5. Accepts feedback and regenerates the plan.
6. Provides an admin dashboard.
7. Provides JSON APIs and automatic OpenAPI docs.
8. Includes a local fallback so the UI and tests can run without an API key.

## Requirements

- Python 3.11+
- VS Code
- Internet access for Gemini API calls
- A Gemini API key for real AI generation

## Windows / VS Code setup

Open the project folder in VS Code, then open **Terminal → New Terminal**.

### 1. Create a virtual environment

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use Command Prompt:

```bat
.venv\Scripts\activate
```

### 2. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configure Gemini

Copy `.env.example` to `.env` and replace:

```text
GEMINI_API_KEY=your_gemini_api_key_here
```

You can leave `AI_FALLBACK_ENABLED=true`. If the key is absent or temporarily unavailable, the app can still be demonstrated with deterministic local output.

### 4. Run

```powershell
uvicorn app.main:app --reload
```

Open:

- http://127.0.0.1:8000
- http://127.0.0.1:8000/docs
- http://127.0.0.1:8000/view-all-users

Default local admin token:

```text
fitbuddy-admin
```

Change it in `.env` before using the app outside a local demo.

## Testing

With the virtual environment activated:

```powershell
pytest -q
```

The tests use the local fallback, so they do not consume Gemini API quota.

## API examples

### Generate

POST `/api/generate-workout`

```json
{
  "username": "Anu",
  "user_id": "FB001",
  "age": 20,
  "weight": 60,
  "goal": "muscle gain",
  "intensity": "medium"
}
```

### Feedback

POST `/api/submit-feedback`

```json
{
  "user_id": "FB001",
  "feedback": "Add more cardio and make Friday a recovery day."
}
```

### Admin users

GET:

```text
/api/users?admin_token=fitbuddy-admin
```

## Project tree

```text
FitBuddy/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── schemas.py
│   ├── routes.py
│   ├── services.py
│   ├── gemini_generator.py
│   ├── gemini_flash_generator.py
│   ├── updated_plan.py
│   ├── templates/
│   │   ├── index.html
│   │   ├── result.html
│   │   ├── admin_login.html
│   │   └── all_users.html
│   └── static/
│       └── css/
│           └── style.css
├── tests/
│   └── test_app.py
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

## Safety note

FitBuddy provides general fitness and nutrition information. It is not a medical diagnostic or treatment system. Users with injuries, medical conditions, pregnancy-related concerns, or other special circumstances should consult an appropriately qualified professional before following a new exercise or nutrition program.
