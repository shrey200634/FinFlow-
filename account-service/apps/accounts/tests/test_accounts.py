import pytest
from rest_framework.test import APIClient

from apps.users.models import User


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        email="test@example.com", full_name="Test User", password="secure123"
    )


@pytest.fixture
def auth_client(client, user):
    res = client.post(
        "/api/token/",
        {"email": "test@example.com", "password": "secure123"},
        format="json",
    )
    token = res.data["access"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


@pytest.fixture
def account_payload():
    return {"name": "My Wallet", "currency": "USD", "status": "ACTIVE"}


@pytest.mark.django_db
def test_create_account(auth_client, account_payload):
    res = auth_client.post("/api/accounts/", account_payload, format="json")
    assert res.status_code == 201
    assert res.data["name"] == "My Wallet"
    assert res.data["currency"] == "USD"
    assert res.data["balance"] == "0.00"


@pytest.mark.django_db
def test_list_accounts(auth_client, account_payload):
    auth_client.post("/api/accounts/", account_payload, format="json")
    res = auth_client.get("/api/accounts/")
    assert res.status_code == 200
    assert res.data["count"] == 1


@pytest.mark.django_db
def test_get_account(auth_client, account_payload):
    create = auth_client.post("/api/accounts/", account_payload, format="json")
    uid = create.data["id"]
    res = auth_client.get(f"/api/accounts/{uid}/")
    assert res.status_code == 200
    assert res.data["name"] == "My Wallet"


@pytest.mark.django_db
def test_update_account(auth_client, account_payload):
    create = auth_client.post("/api/accounts/", account_payload, format="json")
    uid = create.data["id"]
    res = auth_client.patch(
        f"/api/accounts/{uid}/", {"name": "Updated Wallet"}, format="json"
    )
    assert res.status_code == 200
    assert res.data["name"] == "Updated Wallet"


@pytest.mark.django_db
def test_soft_delete_account(auth_client, account_payload):
    create = auth_client.post("/api/accounts/", account_payload, format="json")
    uid = create.data["id"]
    res = auth_client.delete(f"/api/accounts/{uid}/")
    assert res.status_code == 204
    res2 = auth_client.get(f"/api/accounts/{uid}/")
    assert res2.status_code == 404


@pytest.mark.django_db
def test_unauthenticated_access(client):
    res = client.get("/api/accounts/")
    assert res.status_code == 401
