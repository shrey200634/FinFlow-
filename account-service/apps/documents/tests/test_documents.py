from io import BytesIO
from unittest.mock import patch

import pytest
from rest_framework.test import APIClient

from apps.accounts.models import Account
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
def account(user):
    return Account.objects.create(
        user=user, name="My Wallet", currency="USD", status="ACTIVE"
    )


def make_file(name="test.pdf", content_type="application/pdf", size=1024):
    file = BytesIO(b"x" * size)
    file.name = name
    file.content_type = content_type
    file.size = size
    return file


@pytest.mark.django_db
@patch("apps.documents.views.upload_file")
def test_upload_document(mock_upload, auth_client, account):
    mock_upload.return_value = ("finflow-docs", "some/key/test.pdf")
    file = make_file()
    res = auth_client.post(
        "/api/documents/upload/",
        {
            "file": file,
            "doc_type": "ID_PROOF",
            "account": str(account.id),
        },
        format="multipart",
    )
    assert res.status_code == 201
    assert res.data["filename"] == "test.pdf"
    assert res.data["doc_type"] == "ID_PROOF"
    mock_upload.assert_called_once()


@pytest.mark.django_db
@patch("apps.documents.views.upload_file")
def test_invalid_file_type(mock_upload, auth_client, account):
    file = make_file(name="test.exe", content_type="application/exe")
    res = auth_client.post(
        "/api/documents/upload/",
        {
            "file": file,
            "doc_type": "ID_PROOF",
            "account": str(account.id),
        },
        format="multipart",
    )
    assert res.status_code == 400
    mock_upload.assert_not_called()


@pytest.mark.django_db
@patch("apps.documents.views.upload_file")
def test_file_too_large(mock_upload, auth_client, account):
    file = make_file(size=6 * 1024 * 1024)
    res = auth_client.post(
        "/api/documents/upload/",
        {
            "file": file,
            "doc_type": "ID_PROOF",
            "account": str(account.id),
        },
        format="multipart",
    )
    assert res.status_code == 400
    mock_upload.assert_not_called()


@pytest.mark.django_db
@patch("apps.documents.views.upload_file")
def test_upload_wrong_account(mock_upload, auth_client):
    import uuid

    res = auth_client.post(
        "/api/documents/upload/",
        {
            "file": make_file(),
            "doc_type": "ID_PROOF",
            "account": str(uuid.uuid4()),
        },
        format="multipart",
    )
    assert res.status_code == 404
    mock_upload.assert_not_called()


@pytest.mark.django_db
@patch("apps.documents.views.upload_file")
@patch("apps.documents.views.download_file")
def test_download_document(mock_download, mock_upload, auth_client, account):
    mock_upload.return_value = ("finflow-docs", "some/key/test.pdf")
    mock_download.return_value = iter([b"file content"])
    file = make_file()
    upload = auth_client.post(
        "/api/documents/upload/",
        {
            "file": file,
            "doc_type": "ID_PROOF",
            "account": str(account.id),
        },
        format="multipart",
    )
    doc_id = upload.data["id"]
    res = auth_client.get(f"/api/documents/{doc_id}/download/")
    assert res.status_code == 200
    assert res["Content-Disposition"] == 'attachment; filename="test.pdf"'


@pytest.mark.django_db
def test_list_documents(auth_client):
    res = auth_client.get("/api/documents/")
    assert res.status_code == 200


@pytest.mark.django_db
def test_unauthenticated_access(client):
    res = client.get("/api/documents/")
    assert res.status_code == 401
