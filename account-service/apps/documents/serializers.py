from rest_framework import serializers
from .models import Document

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = [
            "id",
            "user",
            "account",
            "doc_type",
            "filename",
            "content_type",
            "file_size",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "filename",
            "content_type",
            "file_size",
            "created_at",
        ]


class DocumentUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    doc_type = serializers.ChoiceField(choices=Document.DOC_TYPES)
    account = serializers.UUIDField()

    def validate_file(self, file):
        if file.content_type not in Document.ALLOWED_TYPES:
            raise serializers.ValidationError(
                "Invalid file type. Allowed: JPEG, PNG, PDF"
            )
        if file.size > MAX_FILE_SIZE:
            raise serializers.ValidationError(
                "File too large. Maximum size is 5MB"
            )
        return file