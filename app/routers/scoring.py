from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.models.scoring import Score
from app.schemas.scoring import ScoreUpdate, ScoreResponse
from app.core.dependencies import get_current_user, get_current_instructor
from app.core.response import success_response
from app.core.exceptions import AppException
from app.services.scoring_service import (
    submit_process_map,
    submit_hazard_analysis,
    submit_fishbone,
    submit_five_whys,
    submit_fmea_pip,
    submit_rca_pip,
    instructor_approve,
)

router = APIRouter()


@router.post("/submit/process-map/{submission_id}")
async def submit_process_map_route(
    submission_id: int,
    course_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    score = await submit_process_map(db, submission_id, current_user.id, course_id)
    return success_response(data=ScoreResponse.model_validate(score).model_dump(), message="Process map submitted")


@router.post("/submit/hazard-analysis/{submission_id}")
async def submit_hazard_analysis_route(
    submission_id: int,
    course_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    score = await submit_hazard_analysis(db, submission_id, current_user.id, course_id)
    return success_response(data=ScoreResponse.model_validate(score).model_dump(), message="Hazard analysis submitted")


@router.post("/submit/fishbone/{submission_id}")
async def submit_fishbone_route(
    submission_id: int,
    course_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    score = await submit_fishbone(db, submission_id, current_user.id, course_id)
    return success_response(data=ScoreResponse.model_validate(score).model_dump(), message="Fishbone submitted")


@router.post("/submit/five-whys/{submission_id}")
async def submit_five_whys_route(
    submission_id: int,
    course_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    score = await submit_five_whys(db, submission_id, current_user.id, course_id)
    return success_response(data=ScoreResponse.model_validate(score).model_dump(), message="5 Whys submitted")


@router.post("/submit/fmea-pip/{submission_id}")
async def submit_fmea_pip_route(
    submission_id: int,
    course_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    score = await submit_fmea_pip(db, submission_id, current_user.id, course_id)
    return success_response(data=ScoreResponse.model_validate(score).model_dump(), message="FMEA PIP submitted")


@router.post("/submit/rca-pip/{submission_id}")
async def submit_rca_pip_route(
    submission_id: int,
    course_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    score = await submit_rca_pip(db, submission_id, current_user.id, course_id)
    return success_response(data=ScoreResponse.model_validate(score).model_dump(), message="RCA PIP submitted")


@router.patch("/{score_id}/review")
async def review_score(
    score_id: int,
    data: ScoreUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_instructor),
):
    score = await instructor_approve(db, score_id, current_user.id, data.instructor_score, data.feedback)
    return success_response(data=ScoreResponse.model_validate(score).model_dump(), message="Score reviewed")


@router.get("/user/{user_id}")
async def get_user_scores(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Score).where(Score.user_id == user_id))
    scores = result.scalars().all()
    return success_response(data=[ScoreResponse.model_validate(s).model_dump() for s in scores])

@router.get("/")
async def get_all_scores(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_instructor),
):
    result = await db.execute(select(Score))
    scores = result.scalars().all()
    return success_response(data=[ScoreResponse.model_validate(s).model_dump() for s in scores])