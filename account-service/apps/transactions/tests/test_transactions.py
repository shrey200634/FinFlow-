import pytest
from unittest.mock import patch
from rest_framework.test import APIClient
from apps.users.models import User
from apps.accounts.models import Account


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        email="test@example.com",
        full_name="Test User",
        password="secure123"
    )


@pytest.fixture
def auth_client(client, user):
    res = client.post("/api/token/", {
        "email": "test@example.com",
        "password": "secure123"
    }, format="json")
    token = res.data["access"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


@pytest.fixture
def account(user):
    return Account.objects.create(
        user=user,
        name="My Wallet",
        currency="USD",
        status="ACTIVE"
    )


@pytest.fixture
def transaction_payload(account):
    return {
        "account": str(account.id),
        "amount": "100.00",
        "transaction_type": "CREDIT",
        "description": "Test payment"
    }


@pytest.mark.django_db
@patch("apps.transactions.views.publish_transaction_created")
def test_create_transaction(mock_publish, auth_client, transaction_payload):
    res = auth_client.post("/api/transactions/", transaction_payload, format="json")
    assert res.status_code == 201
    assert res.data["status"] == "PENDING"
    assert res.data["amount"] == "100.00"
    mock_publish.assert_called_once()


@pytest.mark.django_db
@patch("apps.transactions.views.publish_transaction_created")
def test_list_transactions(mock_publish, auth_client, transaction_payload):
    auth_client.post("/api/transactions/", transaction_payload, format="json")
    res = auth_client.get("/api/transactions/")
    assert res.status_code == 200
    assert res.data["count"] == 1


@pytest.mark.django_db
@patch("apps.transactions.views.publish_transaction_created")
def test_get_transaction(mock_publish, auth_client, transaction_payload):
    create = auth_client.post("/api/transactions/", transaction_payload, format="json")
    uid = create.data["id"]
    res = auth_client.get(f"/api/transactions/{uid}/")
    assert res.status_code == 200
    assert res.data["transaction_type"] == "CREDIT"


@pytest.mark.django_db
@patch("apps.transactions.views.publish_transaction_created")
def test_invalid_amount(mock_publish, auth_client, account):
    payload = {
        "account": str(account.id),
        "amount": "-50.00",
        "transaction_type": "DEBIT",
    }
    res = auth_client.post("/api/transactions/", payload, format="json")
    assert res.status_code == 400


@pytest.mark.django_db
def test_unauthenticated_access(client):
    res = client.get("/api/transactions/")
    assert res.status_code == 401