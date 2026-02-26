from pydantic import BaseModel, ConfigDict
from datetime import datetime


class ScoreCreate(BaseModel):
    user_id: int
    team_id: int | None = None
    course_id: int
    submission_type: str
    process_map_id: int | None = None
    hazard_analysis_id: int | None = None
    fishbone_id: int | None = None
    five_whys_id: int | None = None
    fmea_pip_id: int | None = None
    rca_pip_id: int | None = None
    auto_score: float | None = None
    instructor_score: float | None = None
    feedback: str | None = None


class ScoreUpdate(BaseModel):
    instructor_score: float | None = None
    feedback: str | None = None


class ScoreResponse(BaseModel):
    id: int
    user_id: int
    team_id: int | None
    course_id: int
    submission_type: str
    process_map_id: int | None
    hazard_analysis_id: int | None
    fishbone_id: int | None
    five_whys_id: int | None
    fmea_pip_id: int | None
    rca_pip_id: int | None
    auto_score: float | None
    instructor_score: float | None
    feedback: str | None
    reviewed_by: int | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)