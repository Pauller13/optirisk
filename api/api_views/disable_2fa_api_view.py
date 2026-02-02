from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from base.services.status_service import StatusService

response_status = StatusService()

class Disable2FAView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user
        user.otp_secret = None
        user.is_2fa_enabled = False
        user.save()
        return response_status.status200(data={})
