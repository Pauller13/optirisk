from rest_framework.serializers import ModelSerializer
from user.models.custom_user_model import CustomUserModel


class UpdateUserSerializer(ModelSerializer):

    class Meta:
        model = CustomUserModel
        fields = ['first_name', 'last_name', 'company_name']


