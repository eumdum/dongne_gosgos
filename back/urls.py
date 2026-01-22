# """
# URL configuration for back project.

# The `urlpatterns` list routes URLs to views. For more information please see:
#     https://docs.djangoproject.com/en/5.2/topics/http/urls/
# Examples:
# Function views
#     1. Add an import:  from my_app import views
#     2. Add a URL to urlpatterns:  path('', views.home, name='home')
# Class-based views
#     1. Add an import:  from other_app.views import Home
#     2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
# Including another URLconf
#     1. Import the include() function: from django.urls import include, path
#     2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
# """

# from django.contrib import admin
# from django.urls import path, include
# from django.conf import settings
# from django.conf.urls.static import static
# # from django.http import HttpResponse

# # def home(request):
# #     return HttpResponse("웰켐 Light of Life 프로젝트><")

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('api/', include('store.urls')),  # '/api/'로 시작하는 모든 요청을 store.urls로 전달
#     # path('', home) # 루트페이지 추가
# ]

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# # 목적 : api경로 설정
from django.contrib import admin
from django.urls import path
from store.views import ProductDetectionView, test_upload_page # test_upload_page 추가

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/detect/', ProductDetectionView.as_view(), name='detect'), # 실제 분석 API
    path('test/', test_upload_page, name='test_page'), # 테스트용 화면
]