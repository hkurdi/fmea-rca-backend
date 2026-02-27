from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.gamification import Points, Badge, BadgeType
from app.models.user import User
from app.services.redis_service import increment_leaderboard_score, get_leaderboard


async def award_points(db: AsyncSession, user_id: int, course_id: int, amount: int, reason: str) -> Points:
    points = Points(
        user_id=user_id,
        course_id=course_id,
        amount=amount,
        reason=reason,
    )
    db.add(points)
    await db.flush()
    await increment_leaderboard_score(course_id, user_id, amount)
    return points


async def award_badge(db: AsyncSession, user_id: int, badge_type: BadgeType) -> Badge | None:
    result = await db.execute(
        select(Badge).where(Badge.user_id == user_id, Badge.badge_type == badge_type)
    )
    existing = result.scalar_one_or_none()
    if existing:
        return None

    badge = Badge(user_id=user_id, badge_type=badge_type)
    db.add(badge)
    await db.flush()
    return badge


async def check_and_award_badges(db: AsyncSession, user_id: int, course_id: int) -> list[Badge]:
    awarded = []

    result = await db.execute(
        select(func.count()).select_from(Points).where(
            Points.user_id == user_id,
            Points.course_id == course_id,
        )
    )
    total_submissions = result.scalar()

    if total_submissions == 1:
        badge = await award_badge(db, user_id, BadgeType.FIRST_CASE)
        if badge:
            awarded.append(badge)

    result = await db.execute(
        select(func.count()).select_from(Points).where(
            Points.user_id == user_id,
            Points.reason == "process_map",
        )
    )
    fmea_count = result.scalar()
    if fmea_count >= 3:
        badge = await award_badge(db, user_id, BadgeType.FMEA_MASTER)
        if badge:
            awarded.append(badge)

    result = await db.execute(
        select(func.count()).select_from(Points).where(
            Points.user_id == user_id,
            Points.reason == "fishbone",
        )
    )
    rca_count = result.scalar()
    if rca_count >= 3:
        badge = await award_badge(db, user_id, BadgeType.RCA_MASTER)
        if badge:
            awarded.append(badge)

    return awarded


async def get_course_leaderboard(db: AsyncSession, course_id: int, top_n: int = 10) -> list[dict]:
    entries = await get_leaderboard(course_id, top_n)
    if not entries:
        return []

    # Collect all IDs and fetch users in ONE query
    user_ids = [int(uid_str) for uid_str, _ in entries]
    result = await db.execute(select(User).where(User.id.in_(user_ids)))
    users_map = {u.id: u.full_name for u in result.scalars().all()}

    leaderboard = []
    for rank, (uid_str, score) in enumerate(entries, start=1):
        uid = int(uid_str)
        if uid in users_map:
            leaderboard.append({
                "user_id": uid,
                "full_name": users_map[uid],
                "total_points": int(score),
                "rank": rank,
            })
    return leaderboard