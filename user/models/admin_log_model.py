from django.db import models
from base.helpers.date_time_model import DateTimeModel

class AdminLogModel(DateTimeModel):
    level = models.CharField(max_length=20)
    action = models.CharField(max_length=20)
    message = models.TextField()
