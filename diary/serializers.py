from rest_framework import serializers
from .models import Diary
# from django.contrib.auth.models import User

class DiarySerializer(serializers.ModelSerializer):
    #➡️serializers.ModelSerializer덕뿐에 models.py의 Diary객체를 josn으로 변환하는 수고가 없어짐.
    class Meta: #➡️ DiarySerializer의 설정값을 정의
        model = Diary   #➡️models.py에서 만든 diary객체를 변환대상으로 지정(번역할 원본을 정해줌)
        fields = ['id', 'title', 'content', 'date', 'created_at', 'updated_at', 'emotion']
            #➡️ json으로 변환할때 나열된 7가지 필드만 프론트엔드와 주고받겠다는 말임.
        read_only_fields = ['date', 'created_at', 'updated_at', 'emotion']
            #➡️ 읽기전용! 프론트엔드가 새 일기를 정할때 이 필드는 보내면 안됨
            #➡️ 'date', 'created_at', 'updated_at'는 서버가 알아서 시간을 찍어주는 필드임.
            #➡️ emotion은 서버가 감정분석을 돌려서 채워야 하는 부분임.

        
# 목적 : Django 객체(Diary)를 프론트(Vue)와 주고받기 위해 JSON 형태로 변환해주는 도구

# ModelSerializer를 쓰면 자동으로 모델 필드를 JSON으로 변환해줘
# 프론트에서 보낼 content, Django가 생성할 emotion, created_at을 포함함