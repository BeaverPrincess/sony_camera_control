from django.urls import path
from camera.views import (
    CameraConnectView,
    FetchDeviceDescriptionView,
    CameraControlView,
    SandboxApiSelectionView,
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
    path(
        "sandbox-api-selection/",
        SandboxApiSelectionView.as_view(),
        name="sandbox_api_selection",
    ),
]
