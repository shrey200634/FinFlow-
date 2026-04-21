from django.urls import path 
from . import views


urlpatterns = [
    path("users/", views.UserCreateView.as_view()),
    path("users/<uuid:pk>/", views.UserDetailView.as_view()),
]