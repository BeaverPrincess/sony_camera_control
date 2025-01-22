from django.db import models
from camera.enums import CameraModes


class CameraInfo(models.Model):
    """
    Model for connected cameras.
    """

    model = models.ForeignKey("CameraModel", on_delete=models.SET_NULL, null=True)
    uuid = models.CharField(
        max_length=255,
        unique=True,
    )
    action_list_url = models.URLField(help_text="URL endpoint for API calls.")
    last_connected = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f"{self.model}"


class CameraModel(models.Model):
    """
    Model for supported camera models.
    """

    model = models.CharField(max_length=100, unique=True)
    api_groups = models.ManyToManyField("APIGroup", related_name="camera_models")

    def __str__(self):
        return self.model


class APIGroup(models.Model):
    """
    Model for supported camera API groups.
    """

    group_name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.group_name


class API(models.Model):
    """
    Model for actual APIs.
    """

    api_name = models.CharField(max_length=100)
    group_name = models.ForeignKey(
        "APIGroup", on_delete=models.CASCADE, related_name="apis"
    )
    description = models.TextField(blank=True, null=True)
    json_object = models.JSONField(null=True, blank=True, default=None)
    json_params = models.TextField(null=True, blank=True, default=None)
    service_endpoint = models.CharField(max_length=255)
    required_mode = models.CharField(
        max_length=100,
        choices=CameraModes.choices,
        null=True,
        blank=True,
    )

    def __str__(self):
        if API.objects.filter(api_name=self.api_name).count() > 1:
            return f"{self.api_name} ({self.description})"
        return self.api_name
