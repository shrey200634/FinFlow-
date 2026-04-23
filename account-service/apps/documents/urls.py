from django.urls import path
from . import views

urlpatterns = [
    path("documents/", views.DocumentListView.as_view()),
    path("documents/upload/", views.DocumentUploadView.as_view()),
    path("documents/<uuid:pk>/download/", views.DocumentDownloadView.as_view()),
]