from rest_framework import serializers


class CustomTokenObtainPairSerializer(serializers.Serializer):
    email = serializers.CharField(
        required=True,
        write_only=True
    )
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        trim_whitespace=False
    )
