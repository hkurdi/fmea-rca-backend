from pydantic import BaseModel
from datetime import datetime
from app.models.case import CaseMode


class CaseCreate(BaseModel):
    title: str
    description: str
    patient_info: dict
    mode: CaseMode = CaseMode.EXERCISE
    allow_resubmit: bool = True


class CaseUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    patient_info: dict | None = None
    mode: CaseMode | None = None
    allow_resubmit: bool | None = None
    is_active: bool | None = None


class CaseCourseAssign(BaseModel):
    course_id: int


class CaseResponse(BaseModel):
    id: int
    title: str
    description: str
    patient_info: dict
    mode: CaseMode
    allow_resubmit: bool
    is_active: bool
    created_by: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}