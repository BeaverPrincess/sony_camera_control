from django.db import models


class CameraModes(models.TextChoices):
  Record = "isRecord", "Record"
  StillShoot = "isStillShooting", "Still shooting"
  LiveView = "isLiveView", "Live View"
  
  