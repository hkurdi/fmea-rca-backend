import pytest

pytestmark = pytest.mark.asyncio


async def test_get_all_users_as_admin(client, admin_token):
    response = await client.get("/users/", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert response.json()["success"] is True


async def test_get_all_users_as_student(client, student_token):
    response = await client.get("/users/", headers={"Authorization": f"Bearer {student_token}"})
    assert response.status_code == 403


async def test_get_user_by_id(client, student_token):
    login = await client.post("/auth/login", json={
        "email": "student_test@usf.edu",
        "password": "testpass123",
    })
    user_id = login.json()["data"]
    response = await client.get("/auth/me", headers={"Authorization": f"Bearer {student_token}"})
    user_id = response.json()["data"]["id"]

    response = await client.get(f"/users/{user_id}", headers={"Authorization": f"Bearer {student_token}"})
    assert response.status_code == 200
    assert response.json()["data"]["id"] == user_id


async def test_get_nonexistent_user(client, admin_token):
    response = await client.get("/users/99999", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 404


async def test_update_user(client, student_token):
    response = await client.get("/auth/me", headers={"Authorization": f"Bearer {student_token}"})
    user_id = response.json()["data"]["id"]

    response = await client.put(f"/users/{user_id}", json={
        "full_name": "Updated Name",
    }, headers={"Authorization": f"Bearer {student_token}"})
    assert response.status_code == 200
    assert response.json()["data"]["full_name"] == "Updated Name"


async def test_update_other_user_as_student(client, student_token):
    response = await client.put("/users/1", json={
        "full_name": "Hacked Name",
    }, headers={"Authorization": f"Bearer {student_token}"})
    assert response.status_code == 403


async def test_update_role_as_admin(client, admin_token):
    reg = await client.post("/auth/register", json={
        "email": "roletest@usf.edu",
        "password": "testpass123",
        "full_name": "Role Test",
    })
    user_id = reg.json()["data"]["id"]

    response = await client.patch(f"/users/{user_id}/role", params={"role": "instructor"},
                                   headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert response.json()["data"]["role"] == "instructor"


async def test_deactivate_user_as_admin(client, admin_token):
    reg = await client.post("/auth/register", json={
        "email": "deactivate@usf.edu",
        "password": "testpass123",
        "full_name": "Deactivate Test",
    })
    user_id = reg.json()["data"]["id"]

    response = await client.patch(f"/users/{user_id}/deactivate",
                                   headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200


async def test_deactivate_user_as_student(client, student_token):
    response = await client.patch("/users/1/deactivate",
                                   headers={"Authorization": f"Bearer {student_token}"})
    assert response.status_code == 403