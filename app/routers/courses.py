from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.models.course import Course
from app.schemas.course import CourseCreate, CourseUpdate, CourseResponse
from app.core.dependencies import get_current_user, get_current_instructor, get_current_admin
from app.core.response import success_response
from app.core.exceptions import AppException

router = APIRouter()


@router.get("/")
async def get_all_courses(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Course))
    courses = result.scalars().all()
    return success_response(data=[CourseResponse.model_validate(c).model_dump() for c in courses])


@router.get("/{course_id}")
async def get_course(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()
    if not course:
        raise AppException("Course not found", 404)
    return success_response(data=CourseResponse.model_validate(course).model_dump())


@router.post("/")
async def create_course(
    data: CourseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_instructor),
):
    course = Course(
        name=data.name,
        description=data.description,
        instructor_id=current_user.id,
    )
    db.add(course)
    await db.flush()
    await db.refresh(course)
    return success_response(
        data=CourseResponse.model_validate(course).model_dump(),
        message="Course created",
        status_code=201,
    )


@router.put("/{course_id}")
async def update_course(
    course_id: int,
    data: CourseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_instructor),
):
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()
    if not course:
        raise AppException("Course not found", 404)
    if course.instructor_id != current_user.id:
        raise AppException("Not authorized", 403)

    if data.name:
        course.name = data.name
    if data.description:
        course.description = data.description

    return success_response(
        data=CourseResponse.model_validate(course).model_dump(),
        message="Course updated",
    )


@router.delete("/{course_id}")
async def delete_course(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()
    if not course:
        raise AppException("Course not found", 404)

    await db.delete(course)
    return success_response(message="Course deleted")