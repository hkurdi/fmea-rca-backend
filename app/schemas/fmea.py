from pydantic import BaseModel
from datetime import datetime
from app.models.fmea import SubmissionStatus


class ProcessMapCreate(BaseModel):
    case_id: int
    team_id: int | None = None
    content: dict


class ProcessMapUpdate(BaseModel):
    content: dict | None = None


class ProcessMapResponse(BaseModel):
    id: int
    case_id: int
    user_id: int
    team_id: int | None
    content: dict
    status: SubmissionStatus
    is_locked: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class HazardAnalysisCreate(BaseModel):
    case_id: int
    team_id: int | None = None
    rows: dict


class HazardAnalysisUpdate(BaseModel):
    rows: dict | None = None


class HazardAnalysisResponse(BaseModel):
    id: int
    case_id: int
    user_id: int
    team_id: int | None
    rows: dict
    status: SubmissionStatus
    is_locked: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class FmeaPipCreate(BaseModel):
    case_id: int
    team_id: int | None = None
    content: dict


class FmeaPipUpdate(BaseModel):
    content: dict | None = None


class FmeaPipResponse(BaseModel):
    id: int
    case_id: int
    user_id: int
    team_id: int | None
    content: dict
    status: SubmissionStatus
    is_locked: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}