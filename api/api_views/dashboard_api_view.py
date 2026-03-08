from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from api.serializers.user_serializer import UserSerializer
from base.services.status_service import StatusService
from user.models.custom_user_model import CustomUserModel
from user.enums.role_enum import RoleEnum
from analysis.models import AnalysisModel
from analysis.enums.status_enum import StatusEnum
from cloudinary.exceptions import NotFound
from django.db.models import Count
from django.utils import timezone

status_service = StatusService()

class DashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            user = CustomUserModel.objects.get(id=request.user.id)
            
            # Check if user is admin
            if user.role == RoleEnum.ADMIN:
                return self._get_admin_dashboard(user)
            else:
                return self._get_user_dashboard(user)
                
        except CustomUserModel.DoesNotExist:
            return status_service.status404(data={"error": "Utilisateur non trouvé"})
        except NotFound as e:
            return status_service.status404(data=str(e))
        except Exception as e:
            return status_service.status500(data=str(e))
    
    def _get_user_dashboard(self, user):
        """Dashboard pour utilisateur normal"""
        try:
            # Récupérer les analyses de l'utilisateur
            analyses = AnalysisModel.objects.filter(user=user, status=True)
            
            # Compter les analyses par statut
            analysis_stats = {
                "total": analyses.count(),
                "draft": analyses.filter(status_analysis=StatusEnum.DRAFT).count(),
                "in_progress": analyses.filter(status_analysis=StatusEnum.IN_PROGRESS).count(),
                "completed": analyses.filter(status_analysis=StatusEnum.COMPLETED).count(),
            }
            
            # Récupérer les analyses récentes (5 dernières)
            recent_analyses = analyses.order_by('-updated_at')[:5]
            
            recent_analyses_data = []
            for analysis in recent_analyses:
                # Calculer le progress en pourcentage des workshops complétés
                workshops = [
                    analysis.workshop1_data,
                    analysis.workshop2_data,
                    analysis.workshop3_data,
                    analysis.workshop4_data,
                    analysis.workshop5_data,
                ]
                filled = sum(1 for w in workshops if w)
                progress = (filled / 5) * 100
                
                recent_analyses_data.append({
                    "id": analysis.id,
                    "title": analysis.title,
                    "organization": analysis.organization,
                    "status": analysis.status_analysis,
                    "type": analysis.type,
                    "created_at": analysis.created_at.isoformat(),
                    "progress": round(progress, 2),
                    "last_updated": analysis.updated_at.isoformat(),
                })
            
            return status_service.status200(data={
                "analyses": analysis_stats,
                "recent_analyses": recent_analyses_data,
            })
        except Exception as e:
            return status_service.status500(data=str(e))
    
    def _get_admin_dashboard(self, user):
        """Dashboard pour admin"""
        try:
            # Platform Overview
            users = CustomUserModel.objects.exclude(role=RoleEnum.ADMIN)
            total_users = users.count()
            
            # Utilisateurs actifs ce mois
            current_month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            active_users = users.filter(
                status=True,
            ).count()
            
            
            # Nouveaux utilisateurs ce mois
            new_users_this_month = users.filter(
                status=True,
                date_joined__gte=current_month_start
            )
            
            # Utilisateurs inactifs
            inactive_users = total_users - active_users
            
            platform_overview = {
                "total_users": total_users,
                "active_users": active_users,
                "new_users_this_month": new_users_this_month.count(),
                "inactive_users": inactive_users,
            }
            
            
            
            # Analyses Stats
            all_analyses = AnalysisModel.objects.filter(status=True)
            
            analyses_stats = {
                "total_analyses": all_analyses.count(),
                "draft": all_analyses.filter(status_analysis=StatusEnum.DRAFT).count(),
                "in_progress": all_analyses.filter(status_analysis=StatusEnum.IN_PROGRESS).count(),
                "completed": all_analyses.filter(status_analysis=StatusEnum.COMPLETED).count(),
            }
            
            # Analyses par type
            analyses_by_type = {}
            type_counts = all_analyses.exclude(type__isnull=True).values('type').annotate(count=Count('id'))
            for item in type_counts:
                analyses_by_type[item['type']] = item['count']
            users_data = UserSerializer(users, many=True).data
            for user_data in users_data:
                user_data['last_login'] = users.filter(email=user_data['email']).first().last_login
                user_analyses = all_analyses.filter(user__email=user_data['email'])
                user_data['analyses_number'] = user_analyses.count()
            return status_service.status200(data={
                "platform_overview": platform_overview,
                'users': users_data,
                "analyses_stats": analyses_stats,
                "analyses_by_type": analyses_by_type,
            })
        except Exception as e:
            return status_service.status500(data=str(e))