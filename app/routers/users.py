from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.user import UserUpdate, UserResponse
from app.core.dependencies import get_current_user, get_current_admin
from app.core.response import success_response
from app.core.exceptions import AppException

router = APIRouter()


@router.get("/")
async def get_all_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return success_response(data=[UserResponse.model_validate(u).model_dump() for u in users])


@router.get("/{user_id}")
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise AppException("User not found", 404)
    return success_response(data=UserResponse.model_validate(user).model_dump())


@router.put("/{user_id}")
async def update_user(
    user_id: int,
    data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.id != user_id and current_user.role != UserRole.ADMIN:
        raise AppException("Not authorized", 403)

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise AppException("User not found", 404)

    if data.full_name:
        user.full_name = data.full_name
    if data.usf_id:
        user.usf_id = data.usf_id

    return success_response(data=UserResponse.model_validate(user).model_dump(), message="User updated")


@router.post("/")
async def create_instructor(
    data: UserResponse,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    raise AppException("Use /auth/register and then promote via PATCH /{user_id}/role", 400)


@router.patch("/{user_id}/role")
async def update_role(
    user_id: int,
    role: UserRole,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise AppException("User not found", 404)

    user.role = role
    return success_response(data=UserResponse.model_validate(user).model_dump(), message="Role updated")


@router.patch("/{user_id}/deactivate")
async def deactivate_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise AppException("User not found", 404)

    user.is_active = False
    return success_response(message="User deactivated")