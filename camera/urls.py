from django.urls import path
from . import views

urlpatterns = [
    path("", views.camera_control, name="camera_control"),
    path("discover/", views.discover_camera, name="discover_camera"),
    path("api-call/", views.api_call, name="api_call"),
]
