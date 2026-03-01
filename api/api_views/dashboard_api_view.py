from rest_framework.views import APIView
from base.services.status_service import StatusService
from user.models.custom_user_model import CustomUserModel
from cloudinary.exceptions import NotFound

status_service = StatusService()
class DashboardAPIView(APIView):
    
    def get(self, request):
        try:
            user = CustomUserModel.objects.get(id=request.user.id)
            
            return status_service.status200(data={
                "analysis_count": 0,
                "vulnerability_count": 0,
                "incident_count": 0,
                "report_count": 0,
            })
        except CustomUserModel.DoesNotExist:
            return status_service.status404(data={"error": "Utilisateur non trouvé"})
        except NotFound as e:
            return status_service.status404(data=str(e))
        except Exception as e:
            return status_service.status500(data=str(e))