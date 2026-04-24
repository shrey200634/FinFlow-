import hashlib
import hmac
import logging
import time
import uuid

logger = logging.getLogger(__name__)

TIMESTAMP_TOLERANCE = 300  # 5 minutes in seconds

_used_nonces: set = set()


def generate_signature(secret: str, timestamp: str, nonce: str, body: str) -> str:
    message = f"{timestamp}:{nonce}:{body}"
    return hmac.new(
        secret.encode(),
        message.encode(),
        hashlib.sha256,
    ).hexdigest()


def generate_headers(secret: str, body: str = "") -> dict:
    timestamp = str(int(time.time()))
    nonce = str(uuid.uuid4())
    signature = generate_signature(secret, timestamp, nonce, body)
    return {
        "X-Timestamp": timestamp,
        "X-Nonce": nonce,
        "X-Signature": signature,
    }


def verify_signature(
    secret: str, timestamp: str, nonce: str, body: str, signature: str
) -> bool:
    # Check timestamp tolerance
    try:
        ts = int(timestamp)
    except ValueError:
        logger.warning("Invalid timestamp in HMAC verification")
        return False

    now = int(time.time())
    if abs(now - ts) > TIMESTAMP_TOLERANCE:
        logger.warning("HMAC timestamp too old or too far in future")
        return False

    # Check nonce replay
    if nonce in _used_nonces:
        logger.warning("Replay attack detected — nonce already used")
        return False

    # Verify signature
    expected = generate_signature(secret, timestamp, nonce, body)
    valid = hmac.compare_digest(expected, signature)

    if valid:
        _used_nonces.add(nonce)

    return valid
