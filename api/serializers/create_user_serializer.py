from rest_framework.serializers import ModelSerializer
from user.models.custom_user_model import CustomUserModel


class CreateUserSerializer(ModelSerializer):

    class Meta:
        model = CustomUserModel
        fields = ['email', 'password', 'first_name', 'last_name', 'company_name']
        extra_kwargs = {
            'password': {'write_only': True},
        }

