from django.contrib import admin
from .models import CameraInfo, APIGroup, API, CameraModel


@admin.register(CameraInfo)
class CameraInfoAdmin(admin.ModelAdmin):
    list_display = ("model", "uuid", "action_list_url", "last_connected")


@admin.register(CameraModel)
class CameraModelAdmin(admin.ModelAdmin):
    list_display = ("model", "get_api_groups")

    def get_api_groups(self, obj) -> str:
        return ", ".join([group.group_name for group in obj.api_groups.all()])

    get_api_groups.short_description = "API Groups"


@admin.register(APIGroup)
class APIGroupAdmin(admin.ModelAdmin):
    list_display = ("group_name", "description")


@admin.register(API)
class APIAdmin(admin.ModelAdmin):
    list_display = (
        "api_name",
        "group_name",
        "description",
        "json_object",
        "json_params",
        "service_endpoint",
    )
