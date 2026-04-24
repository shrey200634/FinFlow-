import time

from app.config import HMAC_SECRET
from app.hmac_auth import generate_headers, generate_signature, verify_signature


def test_generate_signature():
    sig = generate_signature("secret", "12345", "nonce1", "body")
    assert isinstance(sig, str)
    assert len(sig) == 64


def test_generate_headers():
    headers = generate_headers(HMAC_SECRET, "test body")
    assert "X-Timestamp" in headers
    assert "X-Nonce" in headers
    assert "X-Signature" in headers


def test_verify_valid_signature():
    headers = generate_headers(HMAC_SECRET, "test body")
    result = verify_signature(
        HMAC_SECRET,
        headers["X-Timestamp"],
        headers["X-Nonce"],
        "test body",
        headers["X-Signature"],
    )
    assert result is True


def test_reject_replay_attack():
    headers = generate_headers(HMAC_SECRET, "test body")
    verify_signature(
        HMAC_SECRET,
        headers["X-Timestamp"],
        headers["X-Nonce"],
        "test body",
        headers["X-Signature"],
    )
    # second use of same nonce should fail
    result = verify_signature(
        HMAC_SECRET,
        headers["X-Timestamp"],
        headers["X-Nonce"],
        "test body",
        headers["X-Signature"],
    )
    assert result is False


def test_reject_stale_timestamp():
    old_timestamp = str(int(time.time()) - 400)
    nonce = "old-nonce-123"
    sig = generate_signature(HMAC_SECRET, old_timestamp, nonce, "body")
    result = verify_signature(HMAC_SECRET, old_timestamp, nonce, "body", sig)
    assert result is False


def test_reject_bad_signature():
    headers = generate_headers(HMAC_SECRET, "test body")
    result = verify_signature(
        HMAC_SECRET,
        headers["X-Timestamp"],
        headers["X-Nonce"],
        "test body",
        "badsignature123",
    )
    assert result is False


def test_reject_invalid_timestamp():
    result = verify_signature(
        HMAC_SECRET,
        "notanumber",
        "some-nonce",
        "body",
        "somesig",
    )
    assert result is False
