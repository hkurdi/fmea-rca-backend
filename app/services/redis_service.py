import redis.asyncio as redis
from app.config import settings


def _get_client():
    return redis.from_url(settings.REDIS_URL, decode_responses=True)


async def increment_leaderboard_score(course_id: int, user_id: int, amount: int):
    client = _get_client()
    try:
        key = f"leaderboard:{course_id}"
        await client.zincrby(key, amount, str(user_id))
    finally:
        await client.aclose()


async def get_leaderboard(course_id: int, limit: int = 10):
    client = _get_client()
    try:
        key = f"leaderboard:{course_id}"
        return await client.zrevrange(key, 0, limit - 1, withscores=True)
    finally:
        await client.aclose()


async def set_reset_token(email: str, token: str, ttl: int = 900):
    client = _get_client()
    try:
        await client.setex(f"reset:{token}", ttl, email)
    finally:
        await client.aclose()


async def get_reset_token(token: str):
    client = _get_client()
    try:
        return await client.get(f"reset:{token}")
    finally:
        await client.aclose()


async def delete_reset_token(token: str):
    client = _get_client()
    try:
        await client.delete(f"reset:{token}")
    finally:
        await client.aclose()