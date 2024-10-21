from django.urls import path
from .views import (
    CameraConnectView,
    FetchDeviceDescriptionView,
    GetAvailableApiListView,
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
        "get-available-api-list/",
        GetAvailableApiListView.as_view(),
        name="get_available_api_list",
    ),
    path(
        "control-camera/",
        CameraControlView.as_view(),
        name="control_camera",
    ),
]
