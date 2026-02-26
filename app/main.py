from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from app.core.exceptions import (
    AppException,
    app_exception_handler,
    validation_exception_handler,
    not_found_handler,
    internal_error_handler,
)
from app.routers import (
    auth,
    users,
    courses,
    teams,
    cases,
    fmea,
    rca,
    scoring,
    gamification,
)


app = FastAPI(
    title="FMEA & RCA Gamification Platform",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(404, not_found_handler)
app.add_exception_handler(500, internal_error_handler)

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(courses.router, prefix="/courses", tags=["Courses"])
app.include_router(teams.router, prefix="/teams", tags=["Teams"])
app.include_router(cases.router, prefix="/cases", tags=["Cases"])
app.include_router(fmea.router, prefix="/cases", tags=["FMEA"])
app.include_router(rca.router, prefix="/cases", tags=["RCA"])
app.include_router(scoring.router, prefix="/scoring", tags=["Scoring"])
app.include_router(gamification.router, prefix="/gamification", tags=["Gamification"])


@app.get("/health")
async def health_check():
    return {"status": "ok"}