from django.contrib import admin
from .models import CameraInfo, CameraService

@admin.register(CameraInfo)
class CameraInfoAdmin(admin.ModelAdmin):
    list_display = ('friendly_name', 'uuid', 'model', 'action_list_url')

@admin.register(CameraService)
class CameraServiceAdmin(admin.ModelAdmin):
    list_display = ('camera_info', 'service_types')