import pytest

import app as app_module
from app import app as flask_app


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    app_module.tasks.clear()
    app_module.next_id = 1
    with flask_app.test_client() as client:
        yield client


def test_index_returns_greeting_and_version(client):
    response = client.get("/")
    assert response.status_code == 200
    body = response.get_json()
    assert "message" in body
    assert "version" in body


def test_health_is_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_create_and_list_tasks(client):
    created = client.post("/tasks", json={"title": "Learn Docker"})
    assert created.status_code == 201
    assert created.get_json()["id"] == 1

    listed = client.get("/tasks")
    assert [t["title"] for t in listed.get_json()] == ["Learn Docker"]


def test_create_task_without_title_fails(client):
    response = client.post("/tasks", json={})
    assert response.status_code == 400


def test_delete_task(client):
    client.post("/tasks", json={"title": "Temporary"})
    assert client.delete("/tasks/1").status_code == 204
    assert client.delete("/tasks/1").status_code == 404


def test_error_endpoint_returns_500(client):
    assert client.get("/error").status_code == 500


def test_metrics_endpoint_exposes_our_counters(client):
    client.get("/")
    response = client.get("/metrics")
    assert response.status_code == 200
    assert b"app_http_requests_total" in response.data
