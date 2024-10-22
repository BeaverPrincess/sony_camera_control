from django.urls import path
from .views import (
    CameraConnectView,
    FetchDeviceDescriptionView,
    CameraControlView,
)

urlpatterns = [
    path("", CameraConnectView.as_view(), name="connect_camera"),
    path(
        "fetch-device-description/",
        FetchDeviceDescriptionView.as_view(),
        name="fetch_device_description",
    ),
    path(
        "control-camera/",
        CameraControlView.as_view(),
        name="control_camera",
    ),
]
