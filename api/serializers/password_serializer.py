from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from user.models.custom_user_model import CustomUserModel


class PasswordSerializer(ModelSerializer):
    new_password = serializers.CharField(required=True, write_only=True)
    class Meta:
        model = CustomUserModel
        fields = ['password', 'new_password']
        extra_kwargs={
            'password': {'write_only': True},
            'new_password': {'write_only': True},
        }



