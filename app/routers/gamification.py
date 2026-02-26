from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.models.gamification import Points, Badge
from app.schemas.gamification import PointsResponse, BadgeResponse, LeaderboardResponse
from app.core.dependencies import get_current_user
from app.core.response import success_response
from app.services.gamification_service import get_course_leaderboard

router = APIRouter()


@router.get("/leaderboard/{course_id}")
async def get_leaderboard(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entries = await get_course_leaderboard(db, course_id)
    return success_response(data={"course_id": course_id, "entries": entries})


@router.get("/points/me")
async def get_my_points(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Points).where(Points.user_id == current_user.id, Points.course_id == course_id)
    )
    points = result.scalars().all()
    return success_response(data=[PointsResponse.model_validate(p).model_dump() for p in points])


@router.get("/badges/me")
async def get_my_badges(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Badge).where(Badge.user_id == current_user.id))
    badges = result.scalars().all()
    return success_response(data=[BadgeResponse.model_validate(b).model_dump() for b in badges])