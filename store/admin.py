from django.contrib import admin
from .models import Product

# 관리자 페이지에 Store 모델 등록
admin.site.register(Product)