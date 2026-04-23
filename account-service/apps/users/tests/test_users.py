import pytest
from rest_framework.test import APIClient


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def user_payload():
    return {
        "email": "test@example.com",
        "full_name": "Test User",
        "password": "secure123",
    }


@pytest.mark.django_db
def test_create_user(client, user_payload):
    res = client.post("/api/users/", user_payload, format="json")
    assert res.status_code == 201
    assert res.data["email"] == "test@example.com"
    assert "password" not in res.data


@pytest.mark.django_db
def test_get_user(client, user_payload):
    create = client.post("/api/users/", user_payload, format="json")
    uid = create.data["id"]
    res = client.get(f"/api/users/{uid}/")
    assert res.status_code == 200
    assert res.data["full_name"] == "Test User"


@pytest.mark.django_db
def test_update_user(client, user_payload):
    create = client.post("/api/users/", user_payload, format="json")
    uid = create.data["id"]
    res = client.patch(
        f"/api/users/{uid}/", {"full_name": "Updated User"}, format="json"
    )
    assert res.status_code == 200
    assert res.data["full_name"] == "Updated User"


@pytest.mark.django_db
def test_soft_delete_user(client, user_payload):
    create = client.post("/api/users/", user_payload, format="json")
    uid = create.data["id"]
    res = client.delete(f"/api/users/{uid}/")
    assert res.status_code == 204
    res2 = client.get(f"/api/users/{uid}/")
    assert res2.status_code == 404
