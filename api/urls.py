from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.routers import DefaultRouter

from api.api_views import (
    Verify2FAView,
    Setup2FAView,
    Disable2FAView,
    CustomTokenView,
    ia_api,
)
from api.api_views.picture_api_view import PictureAPIView
from api.viewsets import (
    CustomUserViewSet,
    AnalysisViewSet,
)

router = DefaultRouter()

router.register('users',CustomUserViewSet)
router.register('analyses',AnalysisViewSet)

urlpatterns = [
    #PUBLIC
    path('login/', CustomTokenView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)),
    path('active-account', CustomUserViewSet.as_view({'put':'activate_account'}), name='active-account'),
    path('demand-to-reset-password', CustomUserViewSet.as_view({'post':'demand_opt_to_reset_password'}), name='demand-to-reset-password'),
    path('reset-password', CustomUserViewSet.as_view({'put':'reset_password'}), name='reset-password'),
    path('2fa/verify/', Verify2FAView.as_view()),

    #PRIVATE
    path('2fa/setup/', Setup2FAView.as_view()),
    path('2fa/disable/', Disable2FAView.as_view()),
    path('profil', CustomUserViewSet.as_view({'get': 'profil'}), name='profil'),
    path('update-my-profile', CustomUserViewSet.as_view({'put': 'update_my_profile'}), name='update-my-profile'),
    path('update-password', CustomUserViewSet.as_view({'put': 'update_password'}), name='update-password'),
    path('delete-my-account', CustomUserViewSet.as_view({'delete': 'delete_account'}), name='delete-my-account'),
    path('profile-picture', PictureAPIView.as_view(), name='update-profile-picture'),
    path('api/ai/swot/', ia_api.generate_swot_view, name='ai_generate_swot'),
    path('api/ai/scenarios/', ia_api.generate_scenarios_view, name='ai_generate_scenarios'),
    path('api/ai/assets/', ia_api.suggest_assets_view, name='ai_suggest_assets'),
    path('api/ai/measures/', ia_api.generate_measures_view, name='ai_generate_measures'),
]