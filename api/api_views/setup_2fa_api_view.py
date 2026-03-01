import pyotp
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from base.services.status_service import StatusService


response_status = StatusService()


class Setup2FAView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user
        if not user.otp_secret:
            user.generate_otp_secret()
            user.generate_secret_key()
        totp = pyotp.TOTP(user.otp_secret)
        uri = totp.provisioning_uri(name=user.email, issuer_name="Optirisk")
        return response_status.status200(data={"otp_auth_url": uri})
    
    def post(self, request):
        user = request.user
        user.is_2fa_enabled = True
        user.save()
        return response_status.status200(data={"otp_auth_url": uri})
