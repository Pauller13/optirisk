from rest_framework import serializers

from user.models.admin_log_model import AdminLogModel


class AdminLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminLogModel
        fields = '__all__'