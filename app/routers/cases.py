from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.course import Course
from app.models.user import User, UserRole
from app.models.case import Case, CaseCourse
from app.schemas.case import CaseCreate, CaseUpdate, CaseResponse, CaseCourseAssign
from app.core.dependencies import get_current_user, get_current_instructor, get_current_admin
from app.core.response import success_response
from app.core.exceptions import AppException

router = APIRouter()


@router.get("/")
async def get_all_cases(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Case).where(Case.is_active == True))
    cases = result.scalars().all()
    return success_response(data=[CaseResponse.model_validate(c).model_dump() for c in cases])


@router.get("/{case_id}")
async def get_case(
    case_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Case).where(Case.id == case_id))
    case = result.scalar_one_or_none()
    if not case:
        raise AppException("Case not found", 404)
    return success_response(data=CaseResponse.model_validate(case).model_dump())


@router.post("/")
async def create_case(
    data: CaseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_instructor),
):
    case = Case(
        title=data.title,
        description=data.description,
        patient_info=data.patient_info,
        mode=data.mode,
        allow_resubmit=data.allow_resubmit,
        created_by=current_user.id,
    )
    db.add(case)
    await db.flush()
    await db.refresh(case)
    return success_response(
        data=CaseResponse.model_validate(case).model_dump(),
        message="Case created",
        status_code=201,
    )


@router.put("/{case_id}")
async def update_case(
    case_id: int,
    data: CaseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_instructor),
):
    result = await db.execute(select(Case).where(Case.id == case_id))
    case = result.scalar_one_or_none()
    if not case:
        raise AppException("Case not found", 404)
    if case.created_by != current_user.id and current_user.role != UserRole.ADMIN:
        raise AppException("Not authorized", 403)

    if data.title:
        case.title = data.title
    if data.description:
        case.description = data.description
    if data.patient_info:
        case.patient_info = data.patient_info
    if data.mode:
        case.mode = data.mode
    if data.allow_resubmit is not None:
        case.allow_resubmit = data.allow_resubmit
    if data.is_active is not None:
        case.is_active = data.is_active

    return success_response(
        data=CaseResponse.model_validate(case).model_dump(),
        message="Case updated",
    )


@router.delete("/{case_id}")
async def delete_case(
    case_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    result = await db.execute(select(Case).where(Case.id == case_id))
    case = result.scalar_one_or_none()
    if not case:
        raise AppException("Case not found", 404)
    case.is_active = False
    await db.commit()
    return success_response(message="Case deactivated")


@router.post("/{case_id}/assign")
async def assign_case_to_course(
    case_id: int,
    data: CaseCourseAssign,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_instructor),
):
    case = await db.get(Case, case_id)
    if not case:
        raise AppException("Case not found", 404)
    
    if case.created_by != current_user.id and current_user.role != UserRole.ADMIN:
        raise AppException("Not authorized to assign this case", 403)

    result = await db.execute(select(Course).where(Course.id == data.course_id))
    if not result.scalar_one_or_none():
        raise AppException("Course not found", 404)

    result = await db.execute(
        select(CaseCourse).where(
            CaseCourse.case_id == case_id, 
            CaseCourse.course_id == data.course_id
        )
    )
    if result.scalar_one_or_none():
        raise AppException("Case already assigned to this course", 409)

    assignment = CaseCourse(case_id=case_id, course_id=data.course_id)
    db.add(assignment)
    await db.flush()
    return success_response(message="Case assigned to course", status_code=201)