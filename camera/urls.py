from django.urls import path
from camera.views import (
    CameraConnectView,
    FetchDeviceDescriptionView,
    CameraControlView,
    APIListView,
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
    path("api/apis/", APIListView.as_view(), name="api_list"),
]
