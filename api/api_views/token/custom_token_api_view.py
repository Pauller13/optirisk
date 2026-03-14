import logging
from user.enums.role_enum import RoleEnum
from user.models.admin_log_model import AdminLogModel
from base.services.status_service import StatusService
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from api.serializers.token.custom_token_serializer import CustomTokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

logger = logging.getLogger('auth_logger')
User = get_user_model()
status_service = StatusService()

login_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "email": openapi.Schema(
            type=openapi.TYPE_STRING,
            description="Email de l'utilisateur",
        ),
        "password": openapi.Schema(
            type=openapi.TYPE_STRING,
            description="Mot de passe de l'utilisateur",
        ),
    }
)

class CustomTokenView(APIView):
    permission_classes = [AllowAny]

    def get_client_ip(self, request):
        """Extract client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', 'Unknown')
    
    @swagger_auto_schema(request_body=login_schema, responses={200: None})
    def post(self, request, *args, **kwargs):
        # Validate input data
        serializer = CustomTokenObtainPairSerializer(data=request.data)
        if not serializer.is_valid():
            return status_service.status400(
                data=serializer.errors, 
                message="Champs invalides"
            )

        email = serializer.validated_data.get('email')
        password = serializer.validated_data.get('password')
        ip = self.get_client_ip(request)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Use constant-time response to prevent user enumeration
            AdminLogModel.objects.create(
                level="WARNING",
                action="LOGIN",
                message=f"Echec de l'authentification pour l'email '{email}'.",
            )
            return status_service.status401(
                data={}, 
                message="Email ou mot de passe invalide"
            )

        # Check password
        if not user.check_password(password):
            if user.role != RoleEnum.ADMIN:
                AdminLogModel.objects.create(
                    level="WARNING",
                    action="LOGIN",
                    message=f"Echec de l'authentification pour mauvais password pour l'email '{email}'.",
                )
            return status_service.status401(
                data={}, 
                message="Email ou mot de passe invalide"
            )

        # Check if account is active
        if not user.is_active:
            if user.role != RoleEnum.ADMIN:
                AdminLogModel.objects.create(
                    level="WARNING",
                    action="LOGIN",
                    message=f"Echec de l'authentification pour compte inactif '{email}'.",
                )
            return status_service.status401(
                data={}, 
                message="Compte désactivé, veuillez utiliser le lien d'activation envoyé par email."
            )

        if not user.status:
            if user.role != RoleEnum.ADMIN:
                AdminLogModel.objects.create(
                    level="WARNING",
                    action="LOGIN",
                    message=f"Echec de l'authentification pour compte suspendu '{email}' from IP {ip} at {now()}.",
                )
            return status_service.status401(
                data={}, 
                message="Compte suspendu, veuillez contacter l'administrateur."
            )

        # Handle 2FA flow
        if user.is_2fa_enabled:
            if user.role != RoleEnum.ADMIN:
                AdminLogModel.objects.create(
                    level="INFO",
                    action="LOGIN",
                    message=f"Connexion reussie pour l'utilisateur '{user.last_name} {user.first_name}'. Autenthication 2FA requise",
                )
            return status_service.status200(
                data={
                    "two_fa_active": True,
                    "temp_token": user.secret_key  # on garde ce token temporairement,
                }, 
                message="2FA requis"
            )
        if user.role != RoleEnum.ADMIN:
            AdminLogModel.objects.create(
                level="INFO",
                action="LOGIN",
                message=f"Connexion reussie pour l'utilisateur '{user.last_name} {user.first_name}' .",
            )
        # Normal login flow (no 2FA)
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        user.last_login = now()
        user.save()
        return status_service.status200(
            data={
                "two_fa_active": False,
                "token": {
                    "refresh": str(refresh),
                    "access": str(access),
                }
            }, 
            message="Connexion réussie"
        )