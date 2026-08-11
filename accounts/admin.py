from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
# from .models import User

User = get_user_model()

# class MyUserAdmin(UserAdmin):
#     list_display = ('username', 'nickname', 'is_owner')

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'nickname', 'is_owner') # 'owner',)