from rest_framework import serializers
from .models import Account


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = [
            "id",
            "user",
            "name",
            "currency",
            "balance",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "balance", "created_at", "updated_at"]

    def validate_currency(self, value):
        valid = ["USD", "EUR", "GBP", "INR"]
        if value not in valid:
            raise serializers.ValidationError(f"Currency must be one of {valid}")
        return value