from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Transaction
from .serializers import TransactionSerializer
from .kafka_producer import publish_transaction_created


class TransactionListCreateView(generics.ListCreateAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(
            account__user=self.request.user,
            deleted_at__isnull=True
        )

    def perform_create(self, serializer):
        transaction = serializer.save()
        publish_transaction_created(transaction)


class TransactionDetailView(generics.RetrieveAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(
            account__user=self.request.user,
            deleted_at__isnull=True
        )
    