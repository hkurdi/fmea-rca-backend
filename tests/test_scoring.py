import pytest

pytestmark = pytest.mark.asyncio


async def create_case_and_course(client, instructor_token):
    course = await client.post("/courses/", json={"name": "Scoring Course"},
                                headers={"Authorization": f"Bearer {instructor_token}"})
    course_id = course.json()["data"]["id"]

    case = await client.post("/cases/", json={
        "title": "Scoring Case",
        "description": "Test",
        "patient_info": {"name": "Test"},
        "mode": "exercise",
        "allow_resubmit": True,
    }, headers={"Authorization": f"Bearer {instructor_token}"})
    case_id = case.json()["data"]["id"]

    return case_id, course_id


async def test_submit_process_map(client, instructor_token, student_token):
    case_id, course_id = await create_case_and_course(client, instructor_token)

    create = await client.post(f"/cases/{case_id}/fmea/process-map", json={
        "case_id": case_id,
        "content": {"steps": ["step1"]},
    }, headers={"Authorization": f"Bearer {student_token}"})
    submission_id = create.json()["data"]["id"]

    response = await client.post(f"/scoring/submit/process-map/{submission_id}",
                                  params={"course_id": course_id},
                                  headers={"Authorization": f"Bearer {student_token}"})
    assert response.status_code == 200
    assert response.json()["data"]["submission_type"] == "process_map"


async def test_submit_hazard_analysis(client, instructor_token, student_token):
    case_id, course_id = await create_case_and_course(client, instructor_token)

    create = await client.post(f"/cases/{case_id}/fmea/hazard-analysis", json={
        "case_id": case_id,
        "rows": {"processes": []},
    }, headers={"Authorization": f"Bearer {student_token}"})
    submission_id = create.json()["data"]["id"]

    response = await client.post(f"/scoring/submit/hazard-analysis/{submission_id}",
                                  params={"course_id": course_id},
                                  headers={"Authorization": f"Bearer {student_token}"})
    assert response.status_code == 200


async def test_submit_fishbone(client, instructor_token, student_token):
    case_id, course_id = await create_case_and_course(client, instructor_token)

    create = await client.post(f"/cases/{case_id}/rca/fishbone", json={
        "case_id": case_id,
        "problem_statement": "Test problem",
    }, headers={"Authorization": f"Bearer {student_token}"})
    submission_id = create.json()["data"]["id"]

    response = await client.post(f"/scoring/submit/fishbone/{submission_id}",
                                  params={"course_id": course_id},
                                  headers={"Authorization": f"Bearer {student_token}"})
    assert response.status_code == 200


async def test_instructor_review(client, instructor_token, student_token):
    case_id, course_id = await create_case_and_course(client, instructor_token)

    create = await client.post(f"/cases/{case_id}/fmea/process-map", json={
        "case_id": case_id,
        "content": {"steps": ["step1"]},
    }, headers={"Authorization": f"Bearer {student_token}"})
    submission_id = create.json()["data"]["id"]

    submit = await client.post(f"/scoring/submit/process-map/{submission_id}",
                                params={"course_id": course_id},
                                headers={"Authorization": f"Bearer {student_token}"})
    score_id = submit.json()["data"]["id"]

    response = await client.patch(f"/scoring/{score_id}/review", json={
        "instructor_score": 28.0,
        "feedback": "Good work, minor issues with subprocess identification",
    }, headers={"Authorization": f"Bearer {instructor_token}"})
    assert response.status_code == 200
    assert response.json()["data"]["instructor_score"] == 28.0


async def test_get_user_scores(client, student_token):
    me = await client.get("/auth/me", headers={"Authorization": f"Bearer {student_token}"})
    user_id = me.json()["data"]["id"]

    response = await client.get(f"/scoring/user/{user_id}",
                                 headers={"Authorization": f"Bearer {student_token}"})
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)


async def test_submit_locked_submission(client, instructor_token, student_token):
    case_id, course_id = await create_case_and_course(client, instructor_token)

    create = await client.post(f"/cases/{case_id}/fmea/process-map", json={
        "case_id": case_id,
        "content": {"steps": ["step1"]},
    }, headers={"Authorization": f"Bearer {student_token}"})
    submission_id = create.json()["data"]["id"]

    await client.post(f"/scoring/submit/process-map/{submission_id}",
                      params={"course_id": course_id},
                      headers={"Authorization": f"Bearer {student_token}"})

    response = await client.post(f"/scoring/submit/process-map/{submission_id}",
                                  params={"course_id": course_id},
                                  headers={"Authorization": f"Bearer {student_token}"})
    assert response.status_code == 403