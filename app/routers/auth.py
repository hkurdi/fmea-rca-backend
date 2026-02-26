from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserRegister, UserLogin, RefreshTokenRequest, ForgotPasswordRequest, ResetPasswordRequest
from app.services.auth_service import register_user, login_user, refresh_access_token, forgot_password, reset_password
from app.core.response import success_response, error_response
from app.core.dependencies import get_current_user

router = APIRouter()


@router.post("/register")
async def register(data: UserRegister, db: AsyncSession = Depends(get_db)):
    user = await register_user(db, data)
    return success_response(
        data={"id": user.id, "email": user.email, "full_name": user.full_name},
        message="Registration successful",
        status_code=201,
    )


@router.post("/login")
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    tokens = await login_user(db, data.email, data.password)
    return success_response(data=tokens, message="Login successful")


@router.post("/refresh")
async def refresh(data: RefreshTokenRequest):
    tokens = await refresh_access_token(data.refresh_token)
    return success_response(data=tokens, message="Token refreshed")


@router.get("/me")
async def me(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return success_response(data={
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "usf_id": user.usf_id,
        "is_usf": user.is_usf,
        "role": user.role.value,
        "is_active": user.is_active,
    })


@router.post("/forgot-password")
async def forgot_password_route(data: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    await forgot_password(db, data.email)
    return success_response(message="If that email exists, a reset link has been sent")


@router.post("/reset-password")
async def reset_password_route(data: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    await reset_password(db, data.token, data.new_password)
    return success_response(message="Password reset successful")