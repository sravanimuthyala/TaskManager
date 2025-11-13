def test_create_task(client):
    response = client.post(
        "/tasks",
        json={"title": "Test Task", "description": ""}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["description"] == ""
    assert data["completed"] is False


def test_get_tasks(client):
    # Create a task first
    client.post("/tasks", json={"title": "Task1", "description": ""})

    response = client.get("/tasks")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1  # At least one task should exist


def test_update_task(client):
    # Create a task to update
    create_res = client.post(
        "/tasks",
        json={"title": "Old Title", "description": ""}
    )
    task_id = create_res.json()["id"]

    # Update the task
    update_res = client.put(
        f"/tasks/{task_id}",
        json={"title": "Updated", "description": "", "completed": True}
    )
    assert update_res.status_code == 200

    data = update_res.json()
    assert data["title"] == "Updated"
    assert data["completed"] is True


def test_delete_task(client):
    # Create a task to delete
    create_res = client.post(
        "/tasks",
        json={"title": "Delete Me", "description": ""}
    )
    task_id = create_res.json()["id"]

    # Delete
    delete_res = client.delete(f"/tasks/{task_id}")
    assert delete_res.status_code == 200

    # Try fetching again → should NOT exist
    tasks = client.get("/tasks").json()
    ids = [t["id"] for t in tasks]

    assert task_id not in ids
