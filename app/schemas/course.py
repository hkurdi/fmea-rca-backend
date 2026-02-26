from pydantic import BaseModel
from datetime import datetime


class CourseCreate(BaseModel):
    name: str
    description: str | None = None


class CourseUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class CourseResponse(BaseModel):
    id: int
    name: str
    description: str | None
    instructor_id: int
    created_at: datetime

    model_config = {"from_attributes": True}