from django.urls import path
from . import views

urlpatterns = [
    path("accounts/", views.AccountListCreateView.as_view()),
    path("accounts/<uuid:pk>/", views.AccountDetailView.as_view()),
]