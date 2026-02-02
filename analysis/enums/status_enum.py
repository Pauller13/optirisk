from django.db import models


class StatusEnum(models.TextChoices):
    DRAFT = 'draft', 'Brouillon'
    IN_PROGRESS = 'in_progress', 'En cours'
    COMPLETED = 'completed', 'Terminé'
