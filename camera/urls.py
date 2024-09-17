from django.urls import path
from .views import get_camera_info

urlpatterns = [
    path('get-camera-info/', get_camera_info, name='get_camera_info'),
]