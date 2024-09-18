from django.urls import path
from .views import CameraControlView, FetchDeviceDescriptionView

urlpatterns = [
    path("", CameraControlView.as_view(), name="camera_control"),
    path(
        "fetch-device-description/",
        FetchDeviceDescriptionView.as_view(),
        name="fetch_device_description",
    ),
]
