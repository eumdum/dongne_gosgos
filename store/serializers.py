from rest_framework import serializers
from .models import Store
# from django.contrib.auth.models import User

class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['image', 'id', 'title', 'content', 'date', 'created_at', 'updated_at', 'emotion', 'item', 'price', 'confidence']
        read_only_fields = ['date', 'created_at', 'updated_at', 'emotion']

# class UserSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True)
    
#     class Meta:
#         model = User
#         fields = ['username', 'email', 'password']
    
#     def create(self, validated_data):
#         user = User.objects.create_user(
#             username=validated_data['username'],
#             email=validated_data.get('email', ''),
#             password=validated_data['password']
#         )
#         return user
        
# 목적 : Django 객체(Diary)를 프론트(Vue)와 주고받기 위해 JSON 형태로 변환해주는 도구

# ModelSerializer를 쓰면 자동으로 모델 필드를 JSON으로 변환해줘
# 프론트에서 보낼 content, Django가 생성할 emotion, created_at을 포함함