from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.models.fmea import ProcessMap, HazardAnalysis, FmeaPip, SubmissionStatus
from app.models.case import Case, CaseMode
from app.schemas.fmea import ProcessMapCreate, ProcessMapUpdate, ProcessMapResponse, HazardAnalysisCreate, HazardAnalysisUpdate, HazardAnalysisResponse, FmeaPipCreate, FmeaPipUpdate, FmeaPipResponse
from app.core.dependencies import get_current_user
from app.core.response import success_response
from app.core.exceptions import AppException

router = APIRouter()


async def check_case_and_lock(db: AsyncSession, case_id: int, submission, user_id: int):
    result = await db.execute(select(Case).where(Case.id == case_id))
    case = result.scalar_one_or_none()
    if not case:
        raise AppException("Case not found", 404)
    if submission and submission.is_locked and not case.allow_resubmit:
        raise AppException("Resubmission not allowed", 403)
    if submission and submission.is_locked and case.mode == CaseMode.ASSESSMENT:
        raise AppException("Cannot edit in assessment mode", 403)
    return case


@router.get("/{case_id}/fmea/process-map")
async def get_process_map(
    case_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(ProcessMap).where(ProcessMap.case_id == case_id, ProcessMap.user_id == current_user.id)
    )
    submission = result.scalar_one_or_none()
    if not submission:
        raise AppException("Process map not found", 404)
    return success_response(data=ProcessMapResponse.model_validate(submission).model_dump())


@router.post("/{case_id}/fmea/process-map")
async def create_process_map(
    case_id: int,
    data: ProcessMapCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await check_case_and_lock(db, case_id, None, current_user.id)
    submission = ProcessMap(
        case_id=case_id,
        user_id=current_user.id,
        team_id=data.team_id,
        content=data.content,
    )
    db.add(submission)
    await db.flush()
    await db.refresh(submission)
    return success_response(
        data=ProcessMapResponse.model_validate(submission).model_dump(),
        message="Process map created",
        status_code=201,
    )


@router.put("/{case_id}/fmea/process-map/{submission_id}")
async def update_process_map(
    case_id: int,
    submission_id: int,
    data: ProcessMapUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(ProcessMap).where(ProcessMap.id == submission_id))
    submission = result.scalar_one_or_none()
    if not submission:
        raise AppException("Process map not found", 404)
    await check_case_and_lock(db, case_id, submission, current_user.id)
    if data.content:
        submission.content = data.content
    return success_response(
        data=ProcessMapResponse.model_validate(submission).model_dump(),
        message="Process map updated",
    )


@router.get("/{case_id}/fmea/hazard-analysis")
async def get_hazard_analysis(
    case_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(HazardAnalysis).where(HazardAnalysis.case_id == case_id, HazardAnalysis.user_id == current_user.id)
    )
    submission = result.scalar_one_or_none()
    if not submission:
        raise AppException("Hazard analysis not found", 404)
    return success_response(data=HazardAnalysisResponse.model_validate(submission).model_dump())


@router.post("/{case_id}/fmea/hazard-analysis")
async def create_hazard_analysis(
    case_id: int,
    data: HazardAnalysisCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await check_case_and_lock(db, case_id, None, current_user.id)
    submission = HazardAnalysis(
        case_id=case_id,
        user_id=current_user.id,
        team_id=data.team_id,
        rows=data.rows,
    )
    db.add(submission)
    await db.flush()
    await db.refresh(submission)
    return success_response(
        data=HazardAnalysisResponse.model_validate(submission).model_dump(),
        message="Hazard analysis created",
        status_code=201,
    )


@router.put("/{case_id}/fmea/hazard-analysis/{submission_id}")
async def update_hazard_analysis(
    case_id: int,
    submission_id: int,
    data: HazardAnalysisUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(HazardAnalysis).where(HazardAnalysis.id == submission_id))
    submission = result.scalar_one_or_none()
    if not submission:
        raise AppException("Hazard analysis not found", 404)
    await check_case_and_lock(db, case_id, submission, current_user.id)
    if data.rows:
        submission.rows = data.rows
    return success_response(
        data=HazardAnalysisResponse.model_validate(submission).model_dump(),
        message="Hazard analysis updated",
    )


@router.get("/{case_id}/fmea/pip")
async def get_fmea_pip(
    case_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(FmeaPip).where(FmeaPip.case_id == case_id, FmeaPip.user_id == current_user.id)
    )
    submission = result.scalar_one_or_none()
    if not submission:
        raise AppException("FMEA PIP not found", 404)
    return success_response(data=FmeaPipResponse.model_validate(submission).model_dump())


@router.post("/{case_id}/fmea/pip")
async def create_fmea_pip(
    case_id: int,
    data: FmeaPipCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await check_case_and_lock(db, case_id, None, current_user.id)
    submission = FmeaPip(
        case_id=case_id,
        user_id=current_user.id,
        team_id=data.team_id,
        content=data.content,
    )
    db.add(submission)
    await db.flush()
    await db.refresh(submission)
    return success_response(
        data=FmeaPipResponse.model_validate(submission).model_dump(),
        message="FMEA PIP created",
        status_code=201,
    )


@router.put("/{case_id}/fmea/pip/{submission_id}")
async def update_fmea_pip(
    case_id: int,
    submission_id: int,
    data: FmeaPipUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(FmeaPip).where(FmeaPip.id == submission_id))
    submission = result.scalar_one_or_none()
    if not submission:
        raise AppException("FMEA PIP not found", 404)
    await check_case_and_lock(db, case_id, submission, current_user.id)
    if data.content:
        submission.content = data.content
    return success_response(
        data=FmeaPipResponse.model_validate(submission).model_dump(),
        message="FMEA PIP updated",
    )