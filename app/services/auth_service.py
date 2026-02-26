import secrets
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User, UserRole
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token, is_usf_email
from app.schemas.user import UserRegister
from app.services.redis_service import set_reset_token, get_reset_token, delete_reset_token
from app.services.email_service import send_password_reset_email
from app.core.exceptions import AppException


async def register_user(db: AsyncSession, data: UserRegister) -> User:
    result = await db.execute(select(User).where(User.email == data.email))
    existing = result.scalar_one_or_none()
    if existing:
        raise AppException("Email already registered", 409)

    if data.usf_id:
        result = await db.execute(select(User).where(User.usf_id == data.usf_id))
        existing_usf = result.scalar_one_or_none()
        if existing_usf:
            raise AppException("USF ID already registered", 409)

    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        full_name=data.full_name,
        usf_id=data.usf_id,
        is_usf=is_usf_email(data.email),
        role=UserRole.STUDENT,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def login_user(db: AsyncSession, email: str, password: str) -> dict:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.hashed_password):
        raise AppException("Invalid email or password", 401)

    if not user.is_active:
        raise AppException("Account is inactive", 403)

    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


async def refresh_access_token(refresh_token: str) -> dict:
    try:
        payload = decode_token(refresh_token)
    except ValueError:
        raise AppException("Invalid or expired refresh token", 401)

    if payload.get("type") != "refresh":
        raise AppException("Invalid token type", 401)

    user_id = payload.get("sub")
    access_token = create_access_token({"sub": user_id})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


async def forgot_password(db: AsyncSession, email: str) -> None:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        return

    token = secrets.token_urlsafe(32)
    await set_reset_token(email, token)
    await send_password_reset_email(email, token)


async def reset_password(db: AsyncSession, token: str, new_password: str) -> None:
    email = await get_reset_token(token)
    if not email:
        raise AppException("Invalid or expired reset token", 400)

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        raise AppException("User not found", 404)

    user.hashed_password = hash_password(new_password)
    await delete_reset_token(token)
    await db.commit()