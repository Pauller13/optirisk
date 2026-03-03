import pyotp
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import AccessToken
from base.services.status_service import StatusService
from user.models.custom_user_model import CustomUserModel
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

response_status = StatusService()

schema =  openapi.Schema(
    type=openapi.TYPE_OBJECT,
    description="Verify 2FA body",
    properties={
        "temp_token": openapi.Schema(
            type=openapi.TYPE_STRING,
            description="Token temporaire",
        ),
        "code": openapi.Schema(
            type=openapi.TYPE_STRING,
            description="Code donné par google authenticator",
        ),
    }
)


class Verify2FAView(APIView):
    permission_classes = [AllowAny]
    @swagger_auto_schema(request_body=schema, responses={200: None})
    def post(self, request):
        token = request.data.get('temp_token')
        code = request.data.get('code')

        try:

            user = CustomUserModel.objects.get(secret_key=token)
        except Exception:
            return response_status.status400(
                data={},
                message="Invalid code or invalid token"
            )

        if not user.is_2fa_enabled or not user.otp_secret:
            return response_status.status400(data={}, message="2FA non activée pour cet utilisateur")

        totp = pyotp.TOTP(user.otp_secret)
        if totp.verify(code):
            # Générer un vrai token JWT
            from rest_framework_simplejwt.tokens import RefreshToken
            refresh = RefreshToken.for_user(user)
            access = refresh.access_token
            return response_status.status200(
                data={
                    "refresh": str(refresh),
                    "access": str(access),
                }
            )
        return response_status.status400(data={}, message="Code incorrect.")
