from django.urls import path
from . import views

urlpatterns = [
    path("", views.camera_control, name="camera_control"),
    path(
        "fetch-device-description/",
        views.fetch_device_description,
        name="fetch_device_description",
    ),
]
