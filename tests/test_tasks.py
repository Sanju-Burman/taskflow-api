import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_task(client: AsyncClient, auth_headers: dict):
    payload = {
        "title": "Build Architecture Plan",
        "description": "Create FastAPI layered architecture specification",
        "status": "in_progress",
        "priority": "high",
    }
    response = await client.post("/api/v1/tasks", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["title"] == "Build Architecture Plan"
    assert data["data"]["status"] == "in_progress"
    assert data["data"]["priority"] == "high"
    assert "id" in data["data"]


@pytest.mark.asyncio
async def test_list_tasks_and_pagination(client: AsyncClient, auth_headers: dict):
    # Create 3 tasks
    for i in range(1, 4):
        await client.post(
            "/api/v1/tasks",
            json={
                "title": f"Task {i}",
                "description": f"Description {i}",
                "status": "pending" if i % 2 == 1 else "completed",
                "priority": "low" if i == 1 else "high",
            },
            headers=auth_headers,
        )

    # List all
    response = await client.get("/api/v1/tasks", headers=auth_headers)
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True
    assert res["pagination"]["total"] == 3
    assert len(res["data"]) == 3

    # Filter by status
    response_filter = await client.get("/api/v1/tasks?status=completed", headers=auth_headers)
    assert response_filter.status_code == 200
    res_filter = response_filter.json()
    assert res_filter["pagination"]["total"] == 1
    assert res_filter["data"][0]["status"] == "completed"

    # Search keyword
    response_search = await client.get("/api/v1/tasks?search=Task 2", headers=auth_headers)
    assert response_search.status_code == 200
    res_search = response_search.json()
    assert res_search["pagination"]["total"] == 1
    assert res_search["data"][0]["title"] == "Task 2"


@pytest.mark.asyncio
async def test_get_task_by_id(client: AsyncClient, auth_headers: dict):
    # Create
    create_res = await client.post(
        "/api/v1/tasks",
        json={"title": "Specific Task", "description": "Details here"},
        headers=auth_headers,
    )
    task_id = create_res.json()["data"]["id"]

    # Retrieve
    get_res = await client.get(f"/api/v1/tasks/{task_id}", headers=auth_headers)
    assert get_res.status_code == 200
    assert get_res.json()["data"]["title"] == "Specific Task"


@pytest.mark.asyncio
async def test_update_and_partial_update_task(client: AsyncClient, auth_headers: dict):
    # Create
    create_res = await client.post(
        "/api/v1/tasks",
        json={"title": "Original Title", "status": "pending"},
        headers=auth_headers,
    )
    task_id = create_res.json()["data"]["id"]

    # Partial update (patch status)
    patch_res = await client.patch(
        f"/api/v1/tasks/{task_id}",
        json={"status": "completed"},
        headers=auth_headers,
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["data"]["status"] == "completed"
    assert patch_res.json()["data"]["title"] == "Original Title"

    # Full update
    put_res = await client.put(
        f"/api/v1/tasks/{task_id}",
        json={
            "title": "Completely Updated Title",
            "description": "Updated Description",
            "status": "in_progress",
            "priority": "urgent",
        },
        headers=auth_headers,
    )
    assert put_res.status_code == 200
    assert put_res.json()["data"]["title"] == "Completely Updated Title"
    assert put_res.json()["data"]["priority"] == "urgent"


@pytest.mark.asyncio
async def test_delete_task(client: AsyncClient, auth_headers: dict):
    # Create
    create_res = await client.post(
        "/api/v1/tasks",
        json={"title": "To be deleted"},
        headers=auth_headers,
    )
    task_id = create_res.json()["data"]["id"]

    # Delete
    del_res = await client.delete(f"/api/v1/tasks/{task_id}", headers=auth_headers)
    assert del_res.status_code == 200
    assert del_res.json()["success"] is True

    # Confirm not found
    get_res = await client.get(f"/api/v1/tasks/{task_id}", headers=auth_headers)
    assert get_res.status_code == 404


@pytest.mark.asyncio
async def test_user_task_isolation_and_security(
    client: AsyncClient,
    auth_headers: dict,
    second_auth_headers: dict,
):
    # User 1 creates a task
    create_res = await client.post(
        "/api/v1/tasks",
        json={"title": "User 1 Private Task"},
        headers=auth_headers,
    )
    user1_task_id = create_res.json()["data"]["id"]

    # User 2 tries to read User 1's task -> 404 Not Found
    get_res = await client.get(f"/api/v1/tasks/{user1_task_id}", headers=second_auth_headers)
    assert get_res.status_code == 404

    # User 2 tries to delete User 1's task -> 404 Not Found
    del_res = await client.delete(f"/api/v1/tasks/{user1_task_id}", headers=second_auth_headers)
    assert del_res.status_code == 404

    # User 2 lists tasks -> should not see User 1's task
    list_res = await client.get("/api/v1/tasks", headers=second_auth_headers)
    assert list_res.status_code == 200
    assert list_res.json()["pagination"]["total"] == 0
