from unittest.mock import patch

import pytest


pytestmark = pytest.mark.asyncio


async def test_register_student(client):
    response = await client.post("/auth/register", json={
        "email": "newstudent@usf.edu",
        "password": "testpass123",
        "full_name": "New Student",
        "usf_id": "U99999999",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["email"] == "newstudent@usf.edu"


async def test_register_non_usf(client):
    response = await client.post("/auth/register", json={
        "email": "external@gmail.com",
        "password": "testpass123",
        "full_name": "External User",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True


async def test_register_duplicate_email(client):
    await client.post("/auth/register", json={
        "email": "duplicate@usf.edu",
        "password": "testpass123",
        "full_name": "Duplicate User",
    })
    response = await client.post("/auth/register", json={
        "email": "duplicate@usf.edu",
        "password": "testpass123",
        "full_name": "Duplicate User",
    })
    assert response.status_code == 409
    assert response.json()["success"] is False


async def test_register_duplicate_usf_id(client):
    await client.post("/auth/register", json={
        "email": "first@usf.edu",
        "password": "testpass123",
        "full_name": "First User",
        "usf_id": "U11111111",
    })
    response = await client.post("/auth/register", json={
        "email": "second@usf.edu",
        "password": "testpass123",
        "full_name": "Second User",
        "usf_id": "U11111111",
    })
    assert response.status_code == 409
    assert response.json()["success"] is False


async def test_login_success(client):
    await client.post("/auth/register", json={
        "email": "logintest@usf.edu",
        "password": "testpass123",
        "full_name": "Login Test",
    })
    response = await client.post("/auth/login", json={
        "email": "logintest@usf.edu",
        "password": "testpass123",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data["data"]
    assert "refresh_token" in data["data"]


async def test_login_wrong_password(client):
    await client.post("/auth/register", json={
        "email": "wrongpass@usf.edu",
        "password": "testpass123",
        "full_name": "Wrong Pass",
    })
    response = await client.post("/auth/login", json={
        "email": "wrongpass@usf.edu",
        "password": "wrongpassword",
    })
    assert response.status_code == 401
    assert response.json()["success"] is False


async def test_login_nonexistent_user(client):
    response = await client.post("/auth/login", json={
        "email": "nobody@usf.edu",
        "password": "testpass123",
    })
    assert response.status_code == 401
    assert response.json()["success"] is False


async def test_refresh_token(client):
    await client.post("/auth/register", json={
        "email": "refreshtest@usf.edu",
        "password": "testpass123",
        "full_name": "Refresh Test",
    })
    login = await client.post("/auth/login", json={
        "email": "refreshtest@usf.edu",
        "password": "testpass123",
    })
    refresh_token = login.json()["data"]["refresh_token"]

    response = await client.post("/auth/refresh", json={
        "refresh_token": refresh_token,
    })
    assert response.status_code == 200
    assert "access_token" in response.json()["data"]


async def test_get_me(client, student_token):
    response = await client.get("/auth/me", headers={
        "Authorization": f"Bearer {student_token}"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "email" in data["data"]


async def test_get_me_no_token(client):
    response = await client.get("/auth/me")
    assert response.status_code == 403


async def test_usf_email_detection(client):
    await client.post("/auth/register", json={
        "email": "usfuser@usf.edu",
        "password": "testpass123",
        "full_name": "USF User",
    })
    login = await client.post("/auth/login", json={
        "email": "usfuser@usf.edu",
        "password": "testpass123",
    })
    token = login.json()["data"]["access_token"]
    response = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.json()["data"]["is_usf"] is True

async def test_forgot_password(client):
    email = "forgot@usf.edu"
    await client.post("/auth/register", json={
        "email": email,
        "password": "testpass123",
        "full_name": "Forgot Password",
        "usf_id": "12345678"
    })
    with patch("app.services.auth_service.send_password_reset_email") as mock_email:
        mock_email.return_value = None
        response = await client.post("/auth/forgot-password", json={
            "email": email,
        })

    assert response.status_code == 200
    assert response.json()["success"] is True
    mock_email.assert_called_once()
    args, _ = mock_email.call_args
    assert args[0] == email

async def test_forgot_password_nonexistent_email(client):
    response = await client.post("/auth/forgot-password", json={
        "email": "nonexistent@usf.edu",
    })
    assert response.status_code == 200
    assert response.json()["success"] is True