import pytest

pytestmark = pytest.mark.asyncio


async def setup_course_and_submission(client, instructor_token, student_token):
    course = await client.post("/courses/", json={"name": "Gamification Course"},
                                headers={"Authorization": f"Bearer {instructor_token}"})
    course_id = course.json()["data"]["id"]

    case = await client.post("/cases/", json={
        "title": "Gamification Case",
        "description": "Test",
        "patient_info": {"name": "Test"},
        "mode": "exercise",
        "allow_resubmit": True,
    }, headers={"Authorization": f"Bearer {instructor_token}"})
    case_id = case.json()["data"]["id"]

    create = await client.post(f"/cases/{case_id}/fmea/process-map", json={
        "case_id": case_id,
        "content": {"steps": ["step1"]},
    }, headers={"Authorization": f"Bearer {student_token}"})
    submission_id = create.json()["data"]["id"]

    await client.post(f"/scoring/submit/process-map/{submission_id}",
                      params={"course_id": course_id},
                      headers={"Authorization": f"Bearer {student_token}"})

    return course_id


async def test_get_leaderboard(client, instructor_token, student_token):
    course_id = await setup_course_and_submission(client, instructor_token, student_token)
    response = await client.get(f"/gamification/leaderboard/{course_id}",
                                 headers={"Authorization": f"Bearer {student_token}"})
    assert response.status_code == 200
    assert "entries" in response.json()["data"]


async def test_get_my_points(client, instructor_token, student_token):
    course_id = await setup_course_and_submission(client, instructor_token, student_token)
    response = await client.get("/gamification/points/me",
                                 params={"course_id": course_id},
                                 headers={"Authorization": f"Bearer {student_token}"})
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert len(response.json()["data"]) > 0


async def test_get_my_badges(client, student_token):
    response = await client.get("/gamification/badges/me",
                                 headers={"Authorization": f"Bearer {student_token}"})
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)


async def test_leaderboard_has_student(client, instructor_token, student_token):
    course_id = await setup_course_and_submission(client, instructor_token, student_token)
    me = await client.get("/auth/me", headers={"Authorization": f"Bearer {student_token}"})
    student_id = me.json()["data"]["id"]

    response = await client.get(f"/gamification/leaderboard/{course_id}",
                                 headers={"Authorization": f"Bearer {student_token}"})
    entries = response.json()["data"]["entries"]
    user_ids = [e["user_id"] for e in entries]
    assert student_id in user_ids


async def test_points_awarded_on_submission(client, instructor_token, student_token):
    course_id = await setup_course_and_submission(client, instructor_token, student_token)
    response = await client.get("/gamification/points/me",
                                 params={"course_id": course_id},
                                 headers={"Authorization": f"Bearer {student_token}"})
    total = sum(p["amount"] for p in response.json()["data"])
    assert total >= 30