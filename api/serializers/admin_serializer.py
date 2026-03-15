from rest_framework import serializers

from user.models.admin_log_model import AdminLogModel


class AdminLogSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    
    class Meta:
        model = AdminLogModel
        fields = '__all__'