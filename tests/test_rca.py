import pytest

pytestmark = pytest.mark.asyncio


async def create_test_case(client, instructor_token):
    response = await client.post("/cases/", json={
        "title": "RCA Test Case",
        "description": "Test",
        "patient_info": {"name": "Test Patient"},
        "mode": "exercise",
        "allow_resubmit": True,
    }, headers={"Authorization": f"Bearer {instructor_token}"})
    return response.json()["data"]["id"]


async def test_create_fishbone(client, instructor_token, student_token):
    case_id = await create_test_case(client, instructor_token)
    response = await client.post(f"/cases/{case_id}/rca/fishbone", json={
        "case_id": case_id,
        "problem_statement": "Patient received wrong medication dose",
    }, headers={"Authorization": f"Bearer {student_token}"})
    assert response.status_code == 201
    assert response.json()["data"]["problem_statement"] == "Patient received wrong medication dose"


async def test_get_fishbone(client, instructor_token, student_token):
    case_id = await create_test_case(client, instructor_token)
    await client.post(f"/cases/{case_id}/rca/fishbone", json={
        "case_id": case_id,
        "problem_statement": "Test problem",
    }, headers={"Authorization": f"Bearer {student_token}"})

    response = await client.get(f"/cases/{case_id}/rca/fishbone",
                                 headers={"Authorization": f"Bearer {student_token}"})
    assert response.status_code == 200


async def test_add_fishbone_node(client, instructor_token, student_token):
    case_id = await create_test_case(client, instructor_token)
    fishbone = await client.post(f"/cases/{case_id}/rca/fishbone", json={
        "case_id": case_id,
        "problem_statement": "Test problem",
    }, headers={"Authorization": f"Bearer {student_token}"})
    fishbone_id = fishbone.json()["data"]["id"]

    response = await client.post(f"/cases/{case_id}/rca/fishbone/{fishbone_id}/nodes", json={
        "label": "Communication failure",
        "level": "major",
        "order_index": 0,
    }, headers={"Authorization": f"Bearer {student_token}"})
    assert response.status_code == 201
    assert response.json()["data"]["label"] == "Communication failure"


async def test_add_child_fishbone_node(client, instructor_token, student_token):
    case_id = await create_test_case(client, instructor_token)
    fishbone = await client.post(f"/cases/{case_id}/rca/fishbone", json={
        "case_id": case_id,
        "problem_statement": "Test problem",
    }, headers={"Authorization": f"Bearer {student_token}"})
    fishbone_id = fishbone.json()["data"]["id"]

    parent = await client.post(f"/cases/{case_id}/rca/fishbone/{fishbone_id}/nodes", json={
        "label": "Major Cause",
        "level": "major",
        "order_index": 0,
    }, headers={"Authorization": f"Bearer {student_token}"})
    parent_id = parent.json()["data"]["id"]

    response = await client.post(f"/cases/{case_id}/rca/fishbone/{fishbone_id}/nodes", json={
        "parent_id": parent_id,
        "label": "Primary Cause",
        "level": "primary",
        "order_index": 0,
    }, headers={"Authorization": f"Bearer {student_token}"})
    assert response.status_code == 201
    assert response.json()["data"]["parent_id"] == parent_id


async def test_create_five_whys(client, instructor_token, student_token):
    case_id = await create_test_case(client, instructor_token)
    response = await client.post(f"/cases/{case_id}/rca/five-whys", json={
        "case_id": case_id,
        "problem": "Potassium level increased to 6.8",
        "iterations": {
            "why1": {"question": "Why did potassium increase?", "answer": "Entresto not adjusted"},
            "why2": {"question": "Why was Entresto not adjusted?", "answer": "No daily labs ordered"},
            "why3": {"question": "Why were no labs ordered?", "answer": "Transfer orders incomplete"},
            "why4": {"question": "Why were transfer orders incomplete?", "answer": "No standardized protocol"},
            "why5": {"question": "Why no standardized protocol?", "answer": "Gap in hospital policy"},
        },
    }, headers={"Authorization": f"Bearer {student_token}"})
    assert response.status_code == 201


async def test_create_rca_pip(client, instructor_token, student_token):
    case_id = await create_test_case(client, instructor_token)
    response = await client.post(f"/cases/{case_id}/rca/pip", json={
        "case_id": case_id,
        "content": {
            "problem": "Incomplete transfer orders",
            "plan": "Standardize transfer protocol",
            "resources": "IT, pharmacy, nursing",
            "timeline": "6 months",
            "measure": "Transfer order completion rate",
        },
    }, headers={"Authorization": f"Bearer {student_token}"})
    assert response.status_code == 201


async def test_fishbone_not_found(client, instructor_token, student_token):
    case_id = await create_test_case(client, instructor_token)
    response = await client.get(f"/cases/{case_id}/rca/fishbone",
                                 headers={"Authorization": f"Bearer {student_token}"})
    assert response.status_code == 404