import uuid
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import StreamingHttpResponse
from .models import Document
from .serializers import DocumentSerializer, DocumentUploadSerializer
from .storage import upload_file, download_file
from apps.accounts.models import Account


class DocumentUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = DocumentUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        file = serializer.validated_data["file"]
        doc_type = serializer.validated_data["doc_type"]
        account_id = serializer.validated_data["account"]

        # enforce ownership
        try:
            account = Account.objects.get(
                id=account_id,
                user=request.user,
                deleted_at__isnull=True
            )
        except Account.DoesNotExist:
            return Response(
                {"error": "Account not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        object_key = f"{request.user.id}/{uuid.uuid4()}/{file.name}"

        bucket, key = upload_file(
            file,
            object_key,
            file.content_type,
            file.size
        )

        document = Document.objects.create(
            user=request.user,
            account=account,
            doc_type=doc_type,
            filename=file.name,
            bucket=bucket,
            object_key=key,
            content_type=file.content_type,
            file_size=file.size,
        )

        return Response(
            DocumentSerializer(document).data,
            status=status.HTTP_201_CREATED
        )


class DocumentDownloadView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            document = Document.objects.get(
                id=pk,
                user=request.user,
                deleted_at__isnull=True
            )
        except Document.DoesNotExist:
            return Response(
                {"error": "Document not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        response_data = download_file(document.bucket, document.object_key)

        response = StreamingHttpResponse(
            response_data,
            content_type=document.content_type
        )
        response["Content-Disposition"] = f'attachment; filename="{document.filename}"'
        return response


class DocumentListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        documents = Document.objects.filter(
            user=request.user,
            deleted_at__isnull=True
        )
        serializer = DocumentSerializer(documents, many=True)
        return Response(serializer.data)