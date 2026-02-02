from rest_framework.serializers import ModelSerializer
from user.models.custom_user_model import CustomUserModel


class PictureUserSerializer(ModelSerializer):

    class Meta:
        model = CustomUserModel
        fields = ['picture']

