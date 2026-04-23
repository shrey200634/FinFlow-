from django.db import models
from apps.users.models import BaseModel, User
from apps.accounts.models import Account


class Document(BaseModel):
    ALLOWED_TYPES = ["image/jpeg", "image/png", "application/pdf"]

    DOC_TYPES = [
        ("ID_PROOF", "ID Proof"),
        ("ADDRESS_PROOF", "Address Proof"),
        ("INCOME_PROOF", "Income Proof"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="documents"
    )
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name="documents"
    )
    doc_type = models.CharField(max_length=20, choices=DOC_TYPES)
    filename = models.CharField(max_length=255)
    bucket = models.CharField(max_length=255, default="finflow-docs")
    object_key = models.CharField(max_length=500)
    content_type = models.CharField(max_length=100)
    file_size = models.PositiveIntegerField()

    class Meta:
        db_table = "documents"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.doc_type} - {self.filename}"