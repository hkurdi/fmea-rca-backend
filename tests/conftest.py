import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool
from app.main import app
from app.database import Base, get_db
from app.config import settings


engine_test = create_async_engine(settings.TEST_DATABASE_URL, poolclass=NullPool)
AsyncTestSession = async_sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)


async def override_get_db():
    async with AsyncTestSession() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_db():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="session")
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def db():
    async with AsyncTestSession() as session:
        yield session


@pytest_asyncio.fixture(scope="session")
async def admin_token(client):
    await client.post("/auth/register", json={
        "email": "admin_test@fmea.com",
        "password": "testpass123",
        "full_name": "Test Admin",
    })
    from sqlalchemy import update
    from app.models.user import User, UserRole
    async with AsyncTestSession() as session:
        await session.execute(
            update(User).where(User.email == "admin_test@fmea.com").values(role=UserRole.ADMIN)
        )
        await session.commit()

    response = await client.post("/auth/login", json={
        "email": "admin_test@fmea.com",
        "password": "testpass123",
    })
    return response.json()["data"]["access_token"]


@pytest_asyncio.fixture(scope="session")
async def instructor_token(client):
    await client.post("/auth/register", json={
        "email": "instructor_test@fmea.com",
        "password": "testpass123",
        "full_name": "Test Instructor",
    })
    from sqlalchemy import update
    from app.models.user import User, UserRole
    async with AsyncTestSession() as session:
        await session.execute(
            update(User).where(User.email == "instructor_test@fmea.com").values(role=UserRole.INSTRUCTOR)
        )
        await session.commit()

    response = await client.post("/auth/login", json={
        "email": "instructor_test@fmea.com",
        "password": "testpass123",
    })
    return response.json()["data"]["access_token"]


@pytest_asyncio.fixture(scope="session")
async def student_token(client):
    await client.post("/auth/register", json={
        "email": "student_test@usf.edu",
        "password": "testpass123",
        "full_name": "Test Student",
        "usf_id": "U12345678",
    })
    response = await client.post("/auth/login", json={
        "email": "student_test@usf.edu",
        "password": "testpass123",
    })
    return response.json()["data"]["access_token"]