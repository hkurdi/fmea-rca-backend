# FMEA & RCA Gamification Platform

A gamified learning platform for PharmD students to practice Failure Mode and Effects Analysis (FMEA) and Root Cause Analysis (RCA) on simulated patient cases.

## Tech Stack

- FastAPI
- PostgreSQL 16
- SQLAlchemy 2.0 (async)
- Alembic
- Redis
- Docker

## Prerequisites

- Python 3.11+
- Docker Desktop

## Getting Started

### 1. Clone the repo

```bash
git clone <repo-url>
cd fmea_rca_backend
```

### 2. Create and activate virtual environment

```bash
python -m venv fmea-venv
source fmea-venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Copy the example env file and fill in your values:

```bash
cp .env.example .env
```

### 5. Start Docker services

```bash
docker compose up -d
```

### 6. Run migrations

```bash
alembic upgrade head
```

### 7. Start the server

```bash
uvicorn app.main:app --reload
```

API will be running at `http://localhost:8000`  
Swagger docs at `http://localhost:8000/docs`  
pgAdmin at `http://localhost:5050`

## Roles

| Role | Description |
|------|-------------|
| student | Self-registers, takes cases, earns points |
| instructor | Created by admin, manages cases and courses |
| admin | Full access, manages all users |

## Case Modes

| Mode | Description |
|------|-------------|
| exercise | Save progress, edit freely, resubmit allowed |
| assessment | Sequential sections, read-only after submit, no resubmit |

## Gamification

Points are tied directly to rubric weights:

| Action | Points |
|--------|--------|
| Submit process map | 30 |
| Submit hazard analysis | 16 |
| Submit fishbone | 40 |
| Submit 5 whys | 4 |
| Submit FMEA PIP | 5 |
| Submit RCA PIP | 5 |
| Instructor approves submission | +20 bonus |
| First submission in class | +10 bonus |

## Planned Features

- USF SSO via Shibboleth/SAML
- AI-powered case generation

## API Docs

Available at `/docs` when the server is running.

## Environment Variables

| Variable | Description |
|----------|-------------|
| DATABASE_URL | PostgreSQL async connection string |
| REDIS_URL | Redis connection string |
| SECRET_KEY | JWT signing secret |
| ALGORITHM | JWT algorithm (HS256) |
| ACCESS_TOKEN_EXPIRE_MINUTES | Access token expiry |
| REFRESH_TOKEN_EXPIRE_DAYS | Refresh token expiry |
| RESET_TOKEN_EXPIRE_MINUTES | Password reset token expiry |
| RESEND_API_KEY | Resend email API key |
| RESEND_FROM_EMAIL | Sender email address |
| APP_ENV | development or production |