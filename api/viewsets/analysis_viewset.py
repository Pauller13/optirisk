from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from analysis.models import AnalysisModel
from api.serializers import (
    AnalysisListSerializer,
    AnalysisDetailSerializer,
    AnalysisCreateSerializer,
)
from base.services.status_service import StatusService
from user.enums.role_enum import RoleEnum
from user.models.admin_log_model import AdminLogModel

status_service = StatusService()


class AnalysisViewSet(ModelViewSet):
    queryset = AnalysisModel.objects.all()
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action == 'list':
            return AnalysisListSerializer
        if self.action == 'retrieve':
            return AnalysisDetailSerializer
        if self.action == 'create':
            return AnalysisCreateSerializer
        return AnalysisDetailSerializer

    def partial_update(self, request, *args, **kwargs):
        return status_service.status405(data={})
    
    def list(self, request, *args, **kwargs):
        try:
            if request.user.role == RoleEnum.ADMIN:
                queryset = self.get_queryset().filter()
            else:
                queryset = self.get_queryset().filter(user=request.user, status=True)
            serializer = AnalysisListSerializer(queryset, many=True)
            return status_service.status200(data=serializer.data)
        except Exception as e:
            return status_service.status500(data=str(e))
    
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                return status_service.status400(data=serializer.errors)
            AdminLogModel.objects.create(level="INFO", action="ANALYSIS", message=f"Utilisateur {request.user.last_name} {request.user.first_name} a créé une nouvelle analyse.")
            serializer.save()
            return status_service.status201(data=serializer.data)
        except Exception as e:
            return status_service.status500(data=str(e))
        
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return status_service.status200(data=serializer.data)
        except Exception as e:
            return status_service.status500(data=str(e))
    
    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data)
            if not serializer.is_valid():
                return status_service.status400(data=serializer.errors)
            serializer.save()
            return status_service.status200(data=serializer.data)
        except Exception as e:
            return status_service.status500(data=str(e))
    
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.status = False
            instance.save()
            AdminLogModel.objects.create(level="INFO", action="ANALYSIS", message=f"Utilisateur {request.user.last_name} {request.user.first_name} a supprimé une analyse.")
            return status_service.status204(data={})
        except Exception as e:
            return status_service.status500(data=str(e))
        

    @action(detail=True, methods=['patch'], url_path='update-workshop')
    def update_workshop(self, request, *args, **kwargs):
        try:
            analysis = self.get_object()
            workshop = request.data.get('workshop')
            data = request.data.get('data')

            if workshop not in [1, 2, 3, 4, 5]:
                return status_service.status400(
                    data={'error': 'Workshop invalide'}
                )
            setattr(analysis, f'workshop{workshop}_data', data)
            analysis.update_status()
            analysis.save()
            AdminLogModel.objects.create(level="INFO", action="ANALYSIS", message=f"Utilisateur {request.user.last_name} {request.user.first_name} a fais l'atelier {workshop}.")
            serializer = AnalysisDetailSerializer(analysis)
            if workshop == 5:
                AdminLogModel.objects.create(level="INFO", action="ANALYSIS", message=f"Utilisateur {request.user.last_name} {request.user.first_name} a terminé l'analyse.")
            return status_service.status200(data=serializer.data)
        except AnalysisModel.DoesNotExist:
            return status_service.status400(data={})
        except Exception as e:
            return status_service.status500(data=str(e))
    
    @action(detail=False, methods=['get'], url_path='reports')
    def reports(self, request, *args, **kwargs):
        try:
            if request.user.role == RoleEnum.ADMIN:
                queryset = self.get_queryset().filter(status=True)
            else:
                queryset = self.get_queryset().filter(user=request.user, status=True)
            
            return status_service.status200(data={
                'reports': {
                    'technical': queryset.technical_report,
                    'executive': queryset.executive_report
                },
                'title': queryset.title
                
            })
        except Exception as e:
            return status_service.status500(data=str(e))