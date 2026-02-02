from django.db import models
from base.helpers.date_time_model import DateTimeModel


class TokenUserModel(DateTimeModel):
    user = models.OneToOneField('user.CustomUserModel', on_delete=models.CASCADE)
    token = models.CharField(max_length=200)