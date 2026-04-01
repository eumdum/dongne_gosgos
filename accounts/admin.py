from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# 커스텀 유저 모델을 어드민에서 볼 수 있게 등록
admin.site.register(User, UserAdmin)