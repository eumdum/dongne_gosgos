from django.urls import path, include
from rest_framework.routers import DefaultRouter
# from .views import DiaryListCreateView
from .views import StoreViewSet #, UserRegistrationView
# from django.contrib import admin
# from rest_framework_simplejwt.views import (
#     TokenObtainPairView,
#     TokenRefreshView,
# )
# from diary.views import UserRegistrationView

# urlpatterns = [
#     path('diaries/', DiaryListCreateView.as_view(), name='diary-list-create'),
# ]

# 목적 : api경로 설정

# 라우터를 사용하여 /diaries/ 경로를 설정
router = DefaultRouter()
router.register(r'stores', StoreViewSet) #, basename='store')

# diary 앱과 관련된 URL만 남겨두고 하나로 합침
urlpatterns = [
    path('', include(router.urls)),

    # # 회원가입 URL (/api/register/)
    # path('register/', UserRegistrationView.as_view(), name='register'), 

    # # JWT 토큰 발급/갱신 URL
    # path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # # DRF 기본 로그인/로그아웃 뷰 (테스트용으로 유용)
    # path('auth/', include('rest_framework.urls')),

]

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('api/diary/', include('diary.urls')),
#     path('api-auth/', include('rest_framework.urls')),
#     path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
#     path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
#     path('api/register/', UserRegistrationView.as_view(), name='register'),
# ]