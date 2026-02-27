from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.scoring import Score
from app.models.fmea import ProcessMap, HazardAnalysis, FmeaPip, SubmissionStatus
from app.models.rca import FishboneDiagram, FiveWhys, RcaPip
from app.models.case import CaseMode
from app.core.exceptions import AppException
from app.services.gamification_service import award_points, check_and_award_badges


SUBMISSION_POINTS = {
    "process_map": 30,
    "hazard_analysis": 16,
    "fishbone": 40,
    "five_whys": 4,
    "fmea_pip": 5,
    "rca_pip": 5,
}

SUBMISSION_REASONS = {
    "process_map": "process_map",
    "hazard_analysis": "hazard_analysis",
    "fishbone": "fishbone",
    "five_whys": "five_whys",
    "fmea_pip": "fmea_pip",
    "rca_pip": "rca_pip",
}


async def submit_process_map(db: AsyncSession, submission_id: int, user_id: int, course_id: int) -> Score:
    result = await db.execute(select(ProcessMap).where(ProcessMap.id == submission_id))
    submission = result.scalar_one_or_none()
    if not submission:
        raise AppException("Process map not found", 404)
    if submission.is_locked:
        raise AppException("Submission is locked", 403)

    submission.status = SubmissionStatus.SUBMITTED
    submission.is_locked = True

    score = Score(
        user_id=user_id,
        course_id=course_id,
        submission_type="process_map",
        process_map_id=submission_id,
        team_id=submission.team_id,
    )
    db.add(score)
    await db.flush()
    await award_points(db, user_id, course_id, SUBMISSION_POINTS["process_map"], SUBMISSION_REASONS["process_map"])
    await check_and_award_badges(db, user_id, course_id)
    return score


async def submit_hazard_analysis(db: AsyncSession, submission_id: int, user_id: int, course_id: int) -> Score:
    result = await db.execute(select(HazardAnalysis).where(HazardAnalysis.id == submission_id))
    submission = result.scalar_one_or_none()
    if not submission:
        raise AppException("Hazard analysis not found", 404)
    if submission.is_locked:
        raise AppException("Submission is locked", 403)

    submission.status = SubmissionStatus.SUBMITTED
    submission.is_locked = True

    score = Score(
        user_id=user_id,
        course_id=course_id,
        submission_type="hazard_analysis",
        hazard_analysis_id=submission_id,
        team_id=submission.team_id,
    )
    db.add(score)
    await db.flush()
    await award_points(db, user_id, course_id, SUBMISSION_POINTS["hazard_analysis"], SUBMISSION_REASONS["hazard_analysis"])
    await check_and_award_badges(db, user_id, course_id)
    return score


async def submit_fishbone(db: AsyncSession, submission_id: int, user_id: int, course_id: int) -> Score:
    result = await db.execute(select(FishboneDiagram).where(FishboneDiagram.id == submission_id))
    submission = result.scalar_one_or_none()
    if not submission:
        raise AppException("Fishbone diagram not found", 404)
    if submission.is_locked:
        raise AppException("Submission is locked", 403)

    submission.status = "submitted"
    submission.is_locked = True

    score = Score(
        user_id=user_id,
        course_id=course_id,
        submission_type="fishbone",
        fishbone_id=submission_id,
        team_id=submission.team_id,
    )
    db.add(score)
    await db.flush()
    await award_points(db, user_id, course_id, SUBMISSION_POINTS["fishbone"], SUBMISSION_REASONS["fishbone"])
    await check_and_award_badges(db, user_id, course_id)
    return score


async def submit_five_whys(db: AsyncSession, submission_id: int, user_id: int, course_id: int) -> Score:
    result = await db.execute(select(FiveWhys).where(FiveWhys.id == submission_id))
    submission = result.scalar_one_or_none()
    if not submission:
        raise AppException("5 Whys not found", 404)
    if submission.is_locked:
        raise AppException("Submission is locked", 403)

    submission.status = "submitted"
    submission.is_locked = True

    score = Score(
        user_id=user_id,
        course_id=course_id,
        submission_type="five_whys",
        five_whys_id=submission_id,
        team_id=submission.team_id,
    )
    db.add(score)
    await db.flush()
    await award_points(db, user_id, course_id, SUBMISSION_POINTS["five_whys"], SUBMISSION_REASONS["five_whys"])
    await check_and_award_badges(db, user_id, course_id)
    return score


async def submit_fmea_pip(db: AsyncSession, submission_id: int, user_id: int, course_id: int) -> Score:
    result = await db.execute(select(FmeaPip).where(FmeaPip.id == submission_id))
    submission = result.scalar_one_or_none()
    if not submission:
        raise AppException("FMEA PIP not found", 404)
    if submission.is_locked:
        raise AppException("Submission is locked", 403)

    submission.status = SubmissionStatus.SUBMITTED
    submission.is_locked = True

    score = Score(
        user_id=user_id,
        course_id=course_id,
        submission_type="fmea_pip",
        fmea_pip_id=submission_id,
        team_id=submission.team_id,
    )
    db.add(score)
    await db.flush()
    await award_points(db, user_id, course_id, SUBMISSION_POINTS["fmea_pip"], SUBMISSION_REASONS["fmea_pip"])
    await check_and_award_badges(db, user_id, course_id)
    return score


async def submit_rca_pip(db: AsyncSession, submission_id: int, user_id: int, course_id: int) -> Score:
    result = await db.execute(select(RcaPip).where(RcaPip.id == submission_id))
    submission = result.scalar_one_or_none()
    if not submission:
        raise AppException("RCA PIP not found", 404)
    if submission.is_locked:
        raise AppException("Submission is locked", 403)

    submission.status = "submitted"
    submission.is_locked = True

    score = Score(
        user_id=user_id,
        course_id=course_id,
        submission_type="rca_pip",
        rca_pip_id=submission_id,
        team_id=submission.team_id,
    )
    db.add(score)
    await db.flush()
    await award_points(db, user_id, course_id, SUBMISSION_POINTS["rca_pip"], SUBMISSION_REASONS["rca_pip"])
    await check_and_award_badges(db, user_id, course_id)
    return score


async def instructor_approve(db: AsyncSession, score_id: int, instructor_id: int, instructor_score: float, feedback: str) -> Score:
    result = await db.execute(select(Score).where(Score.id == score_id))
    score = result.scalar_one_or_none()
    if not score:
        raise AppException("Score not found", 404)

    score.instructor_score = instructor_score
    score.feedback = feedback
    score.reviewed_by = instructor_id

    await award_points(db, score.user_id, score.course_id, 20, "Instructor approved submission")
    return score