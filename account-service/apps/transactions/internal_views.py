import hashlib
import hmac
import logging
import time

from decouple import config
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Transaction

logger = logging.getLogger(__name__)

HMAC_SECRET = config("HMAC_SECRET", default="dev-hmac-secret-change-me")
TIMESTAMP_TOLERANCE = 300
_used_nonces: set = set()


def verify_hmac(request) -> bool:
    timestamp = request.headers.get("X-Timestamp")
    nonce = request.headers.get("X-Nonce")
    signature = request.headers.get("X-Signature")

    if not all([timestamp, nonce, signature]):
        logger.warning("Missing HMAC headers")
        return False

    try:
        ts = int(timestamp)
    except ValueError:
        return False

    if abs(int(time.time()) - ts) > TIMESTAMP_TOLERANCE:
        logger.warning("HMAC timestamp stale")
        return False

    if nonce in _used_nonces:
        logger.warning("Replay attack detected")
        return False

    body = request.body.decode("utf-8")
    message = f"{timestamp}:{nonce}:{body}"
    expected = hmac.new(
        HMAC_SECRET.encode(),
        message.encode(),
        hashlib.sha256,
    ).hexdigest()

    valid = hmac.compare_digest(expected, signature)
    if valid:
        _used_nonces.add(nonce)
    return valid


class InternalTransactionUpdateView(APIView):
    def patch(self, request, pk):
        if not verify_hmac(request):
            return Response(
                {"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            transaction = Transaction.objects.get(id=pk)
        except Transaction.DoesNotExist:
            return Response(
                {"error": "Transaction not found"}, status=status.HTTP_404_NOT_FOUND
            )

        new_status = request.data.get("status")
        if new_status not in ["COMPLETED", "FAILED"]:
            return Response(
                {"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST
            )

        transaction.status = new_status
        transaction.save(update_fields=["status", "updated_at"])
        logger.info(f"Transaction {pk} updated to {new_status}")

        return Response({"id": str(transaction.id), "status": transaction.status})
