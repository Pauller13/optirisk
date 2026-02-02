from django.db import models
from base.helpers.date_time_model import DateTimeModel
from user.enums import OTPTypeEnum


class OTPModel(DateTimeModel):
    user = models.OneToOneField('user.CustomUserModel', on_delete=models.CASCADE)
    code = models.CharField('OTP Code', max_length=6)
    type = models.CharField('OTP Type', max_length=20, choices=OTPTypeEnum.choices())