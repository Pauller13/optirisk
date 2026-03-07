from django.db import models

class RoleEnum(models.TextChoices):
    ADMIN = "admin"
    USER = "user"