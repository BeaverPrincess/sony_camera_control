from django.db import models


class CameraModes(models.TextChoices):
  Record = "record", "Record mode"
  StillShoot = "stillShoot", "Still shooting mode"
  MovieShoot = "movieShoot", "Movie shooting mode"
  