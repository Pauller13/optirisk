from rest_framework.serializers import ModelSerializer
from user.models.custom_user_model import CustomUserModel


class UserSerializer(ModelSerializer):

    class Meta:
        model = CustomUserModel
        fields = ['email', 'first_name', 'last_name', 'company_name', 'created_at', 'updated_at']
        read_only_fields = ['email', 'first_name', 'last_name', 'company_name', 'created_at', 'updated_at']

