from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from api.serializers.admin_serializer import AdminLogSerializer
from user.models.admin_log_model import AdminLogModel
from base.services.status_service import StatusService

status_service = StatusService()

class AdminLogAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            logs = AdminLogModel.objects.all().order_by('-created_at')
            serializer = AdminLogSerializer(logs, many=True)
            return status_service.status200(data=serializer.data)
        except Exception as e:
            return status_service.status500(data=str(e))
        
    def post(self, request, *args, **kwargs):
        try:
            serializer = AdminLogSerializer(data=request.data)
            if not serializer.is_valid():
                return status_service.status400(data=serializer.errors)
            serializer.save()
            return status_service.status201(data=serializer.data)
        except Exception as e:
            return status_service.status500(data=str(e))