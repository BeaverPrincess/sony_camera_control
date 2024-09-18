from django.db import models


class CameraInfo(models.Model):
    friendly_name = models.CharField(max_length=255, help_text="Camera model.")
    uuid = models.CharField(
        max_length=255,
        unique=True,
        help_text="Unique identifier of the camera.",
    )
    model = models.CharField(max_length=255, help_text="Device line.")
    action_list_url = models.URLField(help_text="URL endpoint for API calls.")

    def __str__(self) -> str:
        return f"{self.friendly_name} ({self.model})"


class CameraService(models.Model):
    camera_info = models.ForeignKey(
        CameraInfo,
        on_delete=models.CASCADE,
        related_name="services",
        help_text="The camera to which the services belong.",
    )
    service_types = models.TextField(help_text="List of service types.")

    def set_service_types(self, service_list: list[str]) -> None:
        """Converts a list of services into a comma-separated string for storage."""
        self.service_types = ",".join(service_list)

    def get_service_types(self) -> list[str]:
        """Returns the list of services."""
        return self.service_types.split(",")

    def __str__(self) -> str:
        return f"Services for {self.camera_info.friendly_name}: {self.service_types}"
