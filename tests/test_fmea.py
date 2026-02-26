import pytest

pytestmark = pytest.mark.asyncio


async def create_test_case(client, instructor_token, mode="exercise"):
    response = await client.post("/cases/", json={
        "title": "FMEA Test Case",
        "description": "Test",
        "patient_info": {"name": "Test Patient"},
        "mode": mode,
        "allow_resubmit": True,
    }, headers={"Authorization": f"Bearer {instructor_token}"})
    return response.json()["data"]["id"]


async def test_create_process_map(client, instructor_token, student_token):
    case_id = await create_test_case(client, instructor_token)
    response = await client.post(f"/cases/{case_id}/fmea/process-map", json={
        "case_id": case_id,
        "content": {"steps": ["step1", "step2"]},
    }, headers={"Authorization": f"Bearer {student_token}"})
    assert response.status_code == 201
    assert response.json()["data"]["case_id"] == case_id


async def test_get_process_map(client, instructor_token, student_token):
    case_id = await create_test_case(client, instructor_token)
    await client.post(f"/cases/{case_id}/fmea/process-map", json={
        "case_id": case_id,
        "content": {"steps": ["step1"]},
    }, headers={"Authorization": f"Bearer {student_token}"})

    response = await client.get(f"/cases/{case_id}/fmea/process-map",
                                 headers={"Authorization": f"Bearer {student_token}"})
    assert response.status_code == 200


async def test_update_process_map(client, instructor_token, student_token):
    case_id = await create_test_case(client, instructor_token)
    create = await client.post(f"/cases/{case_id}/fmea/process-map", json={
        "case_id": case_id,
        "content": {"steps": ["step1"]},
    }, headers={"Authorization": f"Bearer {student_token}"})
    submission_id = create.json()["data"]["id"]

    response = await client.put(f"/cases/{case_id}/fmea/process-map/{submission_id}", json={
        "content": {"steps": ["step1", "step2", "step3"]},
    }, headers={"Authorization": f"Bearer {student_token}"})
    assert response.status_code == 200


async def test_create_hazard_analysis(client, instructor_token, student_token):
    case_id = await create_test_case(client, instructor_token)
    response = await client.post(f"/cases/{case_id}/fmea/hazard-analysis", json={
        "case_id": case_id,
        "rows": {"processes": [{"name": "Process 1", "severity": 5, "occurrence": 3, "detection": 2}]},
    }, headers={"Authorization": f"Bearer {student_token}"})
    assert response.status_code == 201


async def test_create_fmea_pip(client, instructor_token, student_token):
    case_id = await create_test_case(client, instructor_token)
    response = await client.post(f"/cases/{case_id}/fmea/pip", json={
        "case_id": case_id,
        "content": {
            "problem": "Medication error",
            "plan": "Implement double check",
            "resources": "Staff training",
            "timeline": "3 months",
            "measure": "Error rate reduction",
        },
    }, headers={"Authorization": f"Bearer {student_token}"})
    assert response.status_code == 201


async def test_process_map_not_found(client, instructor_token, student_token):
    case_id = await create_test_case(client, instructor_token)
    response = await client.get(f"/cases/{case_id}/fmea/process-map",
                                 headers={"Authorization": f"Bearer {student_token}"})
    assert response.status_code == 404