import pytest
import json
import re


def test_api_session_get_sessions(test_client):

    response = test_client.get("/session/")
    assert response.status_code == 200


def test_api_session_redis(test_client):

    response = test_client.get("/session/a")
    assert response.status_code == 200
    assert response.json["a"] == "b"


def test_api_session_post_no_payload(test_client):

    response = test_client.post("/session/")
    assert response.status_code == 415


def test_api_session_post_empty_payload(test_client):

    response = test_client.post("/session/", data=json.dumps([]))
    assert response.status_code == 415


def test_api_session_post_empty_payload_content(test_client):

    response = test_client.post("/session/", data=json.dumps(dict()))
    assert response.status_code == 415


def test_api_session_post(test_client):

    response = test_client.get("/session/")
    actual_sessions = len(response.json)

    response = test_client.post(
        "/session/",
        data=json.dumps(dict(name="test_session_creation")),
        content_type="application/json",
    )
    assert response.status_code == 201
    data = response.json
    assert data["name"] == "test_session_creation"
    assert re.compile(r"[0-9a-fA-F]+$", re.IGNORECASE).match(data["unique_id"])

    response = test_client.get("/session/")
    assert len(response.json) == actual_sessions + 1


def test_api_session_get_nonexistent(test_client):

    response = test_client.get("/session/non_existent_session")
    assert response.status_code == 404


def test_api_session_patch_nonexistent(test_client):
    response = test_client.patch(
        "/session/non_existent_session",
        data=json.dumps(dict(name="new_name")),
        content_type="application/json",
    )
    assert response.status_code == 404


def test_api_session_creation(test_client):

    response = test_client.post(
        "/session/",
        data=json.dumps(dict(name="test_session_functions")),
        content_type="application/json",
    )
    assert response.status_code == 201
    data = response.json
    unique_id = data["unique_id"]
    assert data["name"] == "test_session_functions"

    response = test_client.get(f"/session/{unique_id}")
    assert response.status_code == 200
    data = response.json
    assert data["name"] == "test_session_functions"
    assert data["unique_id"] == unique_id


@pytest.fixture(scope="session")
def session_id(test_client):
    response = test_client.post(
        "/session/",
        data=json.dumps(dict(name="test_session_functions")),
        content_type="application/json",
    )
    return response.json["unique_id"]


def test_api_session_patch_empty_payload_content(test_client, session_id):

    response = test_client.patch(
        f"/session/{session_id}",
        data=json.dumps(dict()),
        content_type="application/json",
    )
    assert response.status_code == 400


def test_api_session_patch_wrong_payload_type(test_client, session_id):

    response = test_client.patch(
        f"/session/{session_id}", data=json.dumps([]), content_type="application/json"
    )
    assert response.status_code == 415


def test_api_session_patch(test_client, session_id):

    response = test_client.patch(
        f"/session/{session_id}",
        data=json.dumps(dict(name="new_name")),
        content_type="application/json",
    )
    assert response.status_code == 204

    response = test_client.get(f"/session/{session_id}")
    assert response.status_code == 200
    assert response.json["name"] == "new_name"
    assert response.json["unique_id"] == session_id


def test_api_session_delete_nonexistent(test_client):

    response = test_client.delete("/session/non_existent_session")
    assert response.status_code == 404


def test_api_session_delete(test_client, session_id):

    response = test_client.delete(f"/session/{session_id}")
    assert response.status_code == 200
