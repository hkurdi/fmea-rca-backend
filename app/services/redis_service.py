import redis.asyncio as aioredis
from app.config import settings

redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)


async def set_reset_token(email: str, token: str) -> None:
    key = f"reset_token:{token}"
    await redis_client.setex(key, settings.RESET_TOKEN_EXPIRE_MINUTES * 60, email)


async def get_reset_token(token: str) -> str | None:
    key = f"reset_token:{token}"
    return await redis_client.get(key)


async def delete_reset_token(token: str) -> None:
    key = f"reset_token:{token}"
    await redis_client.delete(key)


async def set_leaderboard_score(course_id: int, user_id: int, score: int) -> None:
    key = f"leaderboard:{course_id}"
    await redis_client.zadd(key, {str(user_id): score})


async def get_leaderboard(course_id: int, top_n: int = 10) -> list[tuple[str, float]]:
    key = f"leaderboard:{course_id}"
    return await redis_client.zrevrange(key, 0, top_n - 1, withscores=True)


async def increment_leaderboard_score(course_id: int, user_id: int, amount: int) -> None:
    key = f"leaderboard:{course_id}"
    await redis_client.zincrby(key, amount, str(user_id))