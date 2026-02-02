from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from analysis.models import AnalysisModel
from api.serializers import (
    AnalysisListSerializer,
    AnalysisDetailSerializer,
    AnalysisCreateSerializer,
)
from base.services.status_service import StatusService

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

    def getMyAnalysis(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset().filter(user=request.user)
            serializer = AnalysisListSerializer(queryset)
            return status_service.status200(data={serializer.data})
        except Exception as e:
            return status_service.status500(data=str(e))
        
        

    @action(detail=True, methods=['patch'], url_path='update-workshop')
    def update_workshop(self, request, pk=None):
        try:
            analysis = self.get_object()
            workshop = request.data.get('workshop')
            data = request.data.get('data')

            if workshop not in [1, 2, 3, 4, 5]:
                return status_service.status400(
                    data={'error': 'Workshop invalide'}
                )
            setattr(analysis, f'workshop{workshop}_data', data)
            analysis.update_status(analysis)
            analysis.save()
            serializer = AnalysisDetailSerializer(analysis)
            return status_service.status200(data=serializer.data)
        except AnalysisModel.DoesNotExist:
            return status_service.status400(data={})
        except Exception as e:
            return status_service.status500(data=str(e))