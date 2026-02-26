import pytest

pytestmark = pytest.mark.asyncio


async def create_test_course(client, instructor_token):
    response = await client.post("/courses/", json={"name": "Team Test Course"},
                                  headers={"Authorization": f"Bearer {instructor_token}"})
    return response.json()["data"]["id"]


async def test_create_team(client, instructor_token):
    course_id = await create_test_course(client, instructor_token)
    response = await client.post("/teams/", json={
        "name": "Team Alpha",
        "course_id": course_id,
    }, headers={"Authorization": f"Bearer {instructor_token}"})
    assert response.status_code == 201
    assert response.json()["data"]["name"] == "Team Alpha"


async def test_create_team_as_student(client, student_token, instructor_token):
    course_id = await create_test_course(client, instructor_token)
    response = await client.post("/teams/", json={
        "name": "Unauthorized Team",
        "course_id": course_id,
    }, headers={"Authorization": f"Bearer {student_token}"})
    assert response.status_code == 403


async def test_get_all_teams(client, student_token):
    response = await client.get("/teams/", headers={"Authorization": f"Bearer {student_token}"})
    assert response.status_code == 200


async def test_get_team_by_id(client, instructor_token, student_token):
    course_id = await create_test_course(client, instructor_token)
    create = await client.post("/teams/", json={
        "name": "Fetch Team",
        "course_id": course_id,
    }, headers={"Authorization": f"Bearer {instructor_token}"})
    team_id = create.json()["data"]["id"]

    response = await client.get(f"/teams/{team_id}",
                                 headers={"Authorization": f"Bearer {student_token}"})
    assert response.status_code == 200
    assert response.json()["data"]["id"] == team_id


async def test_add_member_to_team(client, instructor_token, student_token):
    course_id = await create_test_course(client, instructor_token)
    team = await client.post("/teams/", json={
        "name": "Member Team",
        "course_id": course_id,
    }, headers={"Authorization": f"Bearer {instructor_token}"})
    team_id = team.json()["data"]["id"]

    me = await client.get("/auth/me", headers={"Authorization": f"Bearer {student_token}"})
    student_id = me.json()["data"]["id"]

    response = await client.post(f"/teams/{team_id}/members", json={
        "user_id": student_id,
    }, headers={"Authorization": f"Bearer {instructor_token}"})
    assert response.status_code == 201


async def test_add_duplicate_member(client, instructor_token, student_token):
    course_id = await create_test_course(client, instructor_token)
    team = await client.post("/teams/", json={
        "name": "Dup Member Team",
        "course_id": course_id,
    }, headers={"Authorization": f"Bearer {instructor_token}"})
    team_id = team.json()["data"]["id"]

    me = await client.get("/auth/me", headers={"Authorization": f"Bearer {student_token}"})
    student_id = me.json()["data"]["id"]

    await client.post(f"/teams/{team_id}/members", json={"user_id": student_id},
                      headers={"Authorization": f"Bearer {instructor_token}"})
    response = await client.post(f"/teams/{team_id}/members", json={"user_id": student_id},
                                  headers={"Authorization": f"Bearer {instructor_token}"})
    assert response.status_code == 409


async def test_remove_member(client, instructor_token, student_token):
    course_id = await create_test_course(client, instructor_token)
    team = await client.post("/teams/", json={
        "name": "Remove Member Team",
        "course_id": course_id,
    }, headers={"Authorization": f"Bearer {instructor_token}"})
    team_id = team.json()["data"]["id"]

    me = await client.get("/auth/me", headers={"Authorization": f"Bearer {student_token}"})
    student_id = me.json()["data"]["id"]

    await client.post(f"/teams/{team_id}/members", json={"user_id": student_id},
                      headers={"Authorization": f"Bearer {instructor_token}"})
    response = await client.delete(f"/teams/{team_id}/members/{student_id}",
                                    headers={"Authorization": f"Bearer {instructor_token}"})
    assert response.status_code == 200