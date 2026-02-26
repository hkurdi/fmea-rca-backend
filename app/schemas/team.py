from pydantic import BaseModel
from datetime import datetime


class TeamCreate(BaseModel):
    name: str
    course_id: int


class TeamUpdate(BaseModel):
    name: str | None = None


class TeamMemberAdd(BaseModel):
    user_id: int


class TeamMemberResponse(BaseModel):
    id: int
    team_id: int
    user_id: int
    joined_at: datetime

    model_config = {"from_attributes": True}


class TeamResponse(BaseModel):
    id: int
    name: str
    course_id: int
    created_at: datetime
    members: list[TeamMemberResponse] = []

    model_config = {"from_attributes": True}