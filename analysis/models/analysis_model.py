import uuid
from django.db import models
from base.helpers.date_time_model import DateTimeModel
from analysis.enums import StatusEnum

class AnalysisModel(DateTimeModel):
    user = models.ForeignKey('user.CustomUserModel', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    organization = models.CharField(max_length=200)
    analysts = models.JSONField(default=list, blank=True, null=True) 
    status_analysis = models.CharField(max_length=20, choices=StatusEnum.choices, default=StatusEnum.DRAFT)
    type = models.CharField(max_length=200)
    context = models.TextField()
    slug = models.SlugField(max_length=100, unique=True)
    workshop1_data = models.JSONField(default=dict, blank=True, null=True)
    workshop2_data = models.JSONField(default=dict, blank=True, null=True)
    workshop3_data = models.JSONField(default=dict, blank=True, null=True)
    workshop4_data = models.JSONField(default=dict, blank=True, null=True)
    workshop5_data = models.JSONField(default=dict, blank=True, null=True)
    
    def save(self, *args, **kwargs):
        is_new = not self.pk
        if is_new:
            self.slug =  f'analysis-{uuid.uuid4().hex}'
        super().save(*args, **kwargs)

    def update_status(self):
        workshops = [
            self.workshop1_data,
            self.workshop2_data,
            self.workshop3_data,
            self.workshop4_data,
            self.workshop5_data,
        ]

        filled = sum(bool(w) for w in workshops)

        if filled == 0:
            self.status_analysis = StatusEnum.DRAFT
        elif filled < 5:
            self.status_analysis = StatusEnum.IN_PROGRESS
        else:
            self.status_analysis = StatusEnum.COMPLETED
