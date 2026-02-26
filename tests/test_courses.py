import pytest

pytestmark = pytest.mark.asyncio


async def test_create_course(client, instructor_token):
    response = await client.post("/courses/", json={
        "name": "Healthcare Innovation IV",
        "description": "FMEA and RCA course",
    }, headers={"Authorization": f"Bearer {instructor_token}"})
    assert response.status_code == 201
    assert response.json()["data"]["name"] == "Healthcare Innovation IV"


async def test_create_course_as_student(client, student_token):
    response = await client.post("/courses/", json={
        "name": "Unauthorized Course",
    }, headers={"Authorization": f"Bearer {student_token}"})
    assert response.status_code == 403


async def test_get_all_courses(client, student_token):
    response = await client.get("/courses/", headers={"Authorization": f"Bearer {student_token}"})
    assert response.status_code == 200
    assert response.json()["success"] is True


async def test_get_course_by_id(client, instructor_token, student_token):
    create = await client.post("/courses/", json={
        "name": "Test Course",
    }, headers={"Authorization": f"Bearer {instructor_token}"})
    course_id = create.json()["data"]["id"]

    response = await client.get(f"/courses/{course_id}",
                                 headers={"Authorization": f"Bearer {student_token}"})
    assert response.status_code == 200
    assert response.json()["data"]["id"] == course_id


async def test_get_nonexistent_course(client, student_token):
    response = await client.get("/courses/99999",
                                 headers={"Authorization": f"Bearer {student_token}"})
    assert response.status_code == 404


async def test_update_course(client, instructor_token):
    create = await client.post("/courses/", json={
        "name": "Old Name",
    }, headers={"Authorization": f"Bearer {instructor_token}"})
    course_id = create.json()["data"]["id"]

    response = await client.put(f"/courses/{course_id}", json={
        "name": "New Name",
    }, headers={"Authorization": f"Bearer {instructor_token}"})
    assert response.status_code == 200
    assert response.json()["data"]["name"] == "New Name"


async def test_delete_course_as_admin(client, admin_token, instructor_token):
    create = await client.post("/courses/", json={
        "name": "To Delete",
    }, headers={"Authorization": f"Bearer {instructor_token}"})
    course_id = create.json()["data"]["id"]

    response = await client.delete(f"/courses/{course_id}",
                                    headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200


async def test_delete_course_as_student(client, student_token):
    response = await client.delete("/courses/1",
                                    headers={"Authorization": f"Bearer {student_token}"})
    assert response.status_code == 403