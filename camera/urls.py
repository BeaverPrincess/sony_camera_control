from django.urls import path
from .views import (
    CameraControlView,
    FetchDeviceDescriptionView,
    GetAvailableApiListView,
)

urlpatterns = [
    path("", CameraControlView.as_view(), name="camera_control"),
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
]
