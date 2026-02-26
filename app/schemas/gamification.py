from pydantic import BaseModel
from datetime import datetime
from app.models.gamification import BadgeType


class PointsResponse(BaseModel):
    id: int
    user_id: int
    course_id: int
    amount: int
    reason: str
    created_at: datetime

    model_config = {"from_attributes": True}


class BadgeResponse(BaseModel):
    id: int
    user_id: int
    badge_type: BadgeType
    earned_at: datetime

    model_config = {"from_attributes": True}


class LeaderboardEntry(BaseModel):
    user_id: int
    full_name: str
    total_points: int
    rank: int


class LeaderboardResponse(BaseModel):
    course_id: int
    entries: list[LeaderboardEntry]