from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models.user import User
from app.models.team import Team, TeamMember
from app.schemas.team import TeamCreate, TeamUpdate, TeamMemberAdd, TeamResponse, TeamMemberResponse
from app.core.dependencies import get_current_user, get_current_instructor
from app.core.response import success_response
from app.core.exceptions import AppException

router = APIRouter()


@router.get("/")
async def get_all_teams(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Team).options(selectinload(Team.members)))
    teams = result.scalars().all()
    return success_response(data=[TeamResponse.model_validate(t).model_dump() for t in teams])


@router.get("/{team_id}")
async def get_team(
    team_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Team).where(Team.id == team_id).options(selectinload(Team.members))
    )
    team = result.scalar_one_or_none()
    if not team:
        raise AppException("Team not found", 404)
    return success_response(data=TeamResponse.model_validate(team).model_dump())


@router.post("/")
async def create_team(
    data: TeamCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_instructor),
):
    team = Team(name=data.name, course_id=data.course_id)
    db.add(team)
    await db.flush()
    result = await db.execute(
        select(Team).options(selectinload(Team.members)).where(Team.id == team.id)
    )
    team = result.scalar_one()
    return success_response(
        data=TeamResponse.model_validate(team).model_dump(), 
        message="Team created", 
        status_code=201
    )


@router.put("/{team_id}")
async def update_team(
    team_id: int,
    data: TeamUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_instructor),
):
    result = await db.execute(
        select(Team).where(Team.id == team_id).options(selectinload(Team.members))
    )
    team = result.scalar_one_or_none()
    if not team:
        raise AppException("Team not found", 404)
    
    if data.name:
        team.name = data.name
    
    await db.flush()
    
    return success_response(
        data=TeamResponse.model_validate(team).model_dump(),
        message="Team updated",
    )


@router.delete("/{team_id}")
async def delete_team(
    team_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_instructor),
):
    result = await db.execute(select(Team).where(Team.id == team_id))
    team = result.scalar_one_or_none()
    if not team:
        raise AppException("Team not found", 404)
    
    await db.delete(team)

    return success_response(message="Team deleted")


@router.post("/{team_id}/members")
async def add_member(
    team_id: int,
    data: TeamMemberAdd,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_instructor),
):
    result = await db.execute(select(Team).where(Team.id == team_id))
    team = result.scalar_one_or_none()
    if not team:
        raise AppException("Team not found", 404)

    result = await db.execute(
        select(TeamMember).where(TeamMember.team_id == team_id, TeamMember.user_id == data.user_id)
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise AppException("User already in team", 409)

    member = TeamMember(team_id=team_id, user_id=data.user_id)
    db.add(member)
    await db.flush()

    await db.refresh(member)
    
    return success_response(
        data=TeamMemberResponse.model_validate(member).model_dump(),
        message="Member added",
        status_code=201,
    )


@router.delete("/{team_id}/members/{user_id}")
async def remove_member(
    team_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_instructor),
):
    result = await db.execute(
        select(TeamMember).where(TeamMember.team_id == team_id, TeamMember.user_id == user_id)
    )
    member = result.scalar_one_or_none()
    if not member:
        raise AppException("Member not found", 404)
    
    await db.delete(member)

    return success_response(message="Member removed")