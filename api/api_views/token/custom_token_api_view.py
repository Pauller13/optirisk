import logging
from base.services.status_service import StatusService
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from api.serializers.token.custom_token_serializer import CustomTokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in
from django.utils.timezone import now
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.settings import api_settings
from datetime import timedelta

logger = logging.getLogger('auth_logger')
User = get_user_model()
status_service = StatusService()

class CustomTokenView(APIView):
    permission_classes = [AllowAny]

    def get_client_ip(self, request):
        """Extract client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', 'Unknown')

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
            logger.warning(
                f"[FAILED LOGIN] Login attempt for non-existent email '{email}' "
                f"from IP {ip} at {now()}."
            )
            return status_service.status401(
                data={}, 
                message="Email ou mot de passe invalide"
            )

        # Check password
        if not user.check_password(password):
            logger.warning(
                f"[FAILED LOGIN] Invalid password for email '{email}' "
                f"from IP {ip} at {now()}."
            )
            return status_service.status401(
                data={}, 
                message="Email ou mot de passe invalide"
            )

        # Check if account is active
        if not user.is_active:
            logger.warning(
                f"[FAILED LOGIN] Inactive account login attempt for '{email}' "
                f"from IP {ip} at {now()}."
            )
            return status_service.status401(
                data={}, 
                message="Compte désactivé, veuillez utiliser le lien d'activation envoyé par email."
            )

        # Successful authentication
        logger.info(
            f"[LOGIN] User '{user.last_name} {user.first_name}' (ID: {user.id}) "
            f"logged in from IP {ip} at {now()}."
        )

        # Handle 2FA flow
        if user.is_2fa_enabled:
            
            return status_service.status200(
                data={
                    "two_fa_active": True,
                    "temp_token": user.secret_key  # on garde ce token temporairement,
                }, 
                message="2FA requis"
            )

        # Normal login flow (no 2FA)
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        # Update last login
        if api_settings.UPDATE_LAST_LOGIN:
            user_logged_in.send(sender=user.__class__, request=request, user=user)

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