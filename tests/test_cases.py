import pytest

pytestmark = pytest.mark.asyncio


async def create_test_case(client, instructor_token):
    response = await client.post("/cases/", json={
        "title": "Test Case",
        "description": "A test patient case",
        "patient_info": {"name": "John Doe", "age": 65},
        "mode": "exercise",
        "allow_resubmit": True,
    }, headers={"Authorization": f"Bearer {instructor_token}"})
    return response.json()["data"]["id"]


async def test_create_case(client, instructor_token):
    response = await client.post("/cases/", json={
        "title": "New Case",
        "description": "Description",
        "patient_info": {"name": "Jane Doe", "age": 70},
        "mode": "exercise",
        "allow_resubmit": True,
    }, headers={"Authorization": f"Bearer {instructor_token}"})
    assert response.status_code == 201
    assert response.json()["data"]["title"] == "New Case"


async def test_create_case_as_student(client, student_token):
    response = await client.post("/cases/", json={
        "title": "Unauthorized",
        "description": "Nope",
        "patient_info": {},
        "mode": "exercise",
        "allow_resubmit": True,
    }, headers={"Authorization": f"Bearer {student_token}"})
    assert response.status_code == 403


async def test_get_all_cases(client, student_token):
    response = await client.get("/cases/", headers={"Authorization": f"Bearer {student_token}"})
    assert response.status_code == 200
    assert response.json()["success"] is True


async def test_get_case_by_id(client, instructor_token, student_token):
    case_id = await create_test_case(client, instructor_token)
    response = await client.get(f"/cases/{case_id}",
                                 headers={"Authorization": f"Bearer {student_token}"})
    assert response.status_code == 200
    assert response.json()["data"]["id"] == case_id


async def test_get_nonexistent_case(client, student_token):
    response = await client.get("/cases/99999",
                                 headers={"Authorization": f"Bearer {student_token}"})
    assert response.status_code == 404


async def test_update_case(client, instructor_token):
    case_id = await create_test_case(client, instructor_token)
    response = await client.put(f"/cases/{case_id}", json={
        "title": "Updated Title",
    }, headers={"Authorization": f"Bearer {instructor_token}"})
    assert response.status_code == 200
    assert response.json()["data"]["title"] == "Updated Title"


async def test_deactivate_case(client, admin_token, instructor_token):
    case_id = await create_test_case(client, instructor_token)
    response = await client.delete(f"/cases/{case_id}",
                                    headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200


async def test_assign_case_to_course(client, instructor_token):
    case_id = await create_test_case(client, instructor_token)
    course = await client.post("/courses/", json={"name": "Assign Course"},
                                headers={"Authorization": f"Bearer {instructor_token}"})
    course_id = course.json()["data"]["id"]

    response = await client.post(f"/cases/{case_id}/assign", json={"course_id": course_id},
                                  headers={"Authorization": f"Bearer {instructor_token}"})
    assert response.status_code == 201


async def test_assign_case_duplicate(client, instructor_token):
    case_id = await create_test_case(client, instructor_token)
    course = await client.post("/courses/", json={"name": "Dup Assign Course"},
                                headers={"Authorization": f"Bearer {instructor_token}"})
    course_id = course.json()["data"]["id"]

    await client.post(f"/cases/{case_id}/assign", json={"course_id": course_id},
                      headers={"Authorization": f"Bearer {instructor_token}"})
    response = await client.post(f"/cases/{case_id}/assign", json={"course_id": course_id},
                                  headers={"Authorization": f"Bearer {instructor_token}"})
    assert response.status_code == 409