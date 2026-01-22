# from django.db import models
# # from django.contrib.auth.models import User
# from datetime import date

# class Diary(models.Model):
#     title = models.CharField(max_length=200, default="기본제목")
#     content = models.TextField(default="")
#     date = models.DateField(default=date.today)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     emotion = models.CharField(max_length=20, blank=True, null=True)
#     # user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='store_entries', null=True)
    
#     class Meta:
#         ordering = ['-date'] # 최신 날짜순으로 정렬
        
#     def __str__(self):
#         return f"{self.title} ({self.date})"

# class Store(models.Model):
#     title = models.CharField(max_length=200, default="기본제목")
#     content = models.TextField(default="")
#     date = models.DateField(default=date.today)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     emotion = models.CharField(max_length=20, blank=True, null=True)
#     item = models.CharField(max_length=100, blank=True, null=True)      # 상품명
#     price = models.IntegerField(blank=True, null=True)                  # 가격
#     confidence = models.FloatField(blank=True, null=True)               # 신뢰도
#     image = models.ImageField(upload_to='uploads/', blank=True, null=True)

#     def __str__(self):
#         return f"{self.created_at} - {self.emotion} - {self.item}"

# # 목적 : 데이터베이스에 저장할 일기 테이블 구조를 정의

# # TextField : 긴 텍스트를 저장하기 적합 (일기 내용)
# # CharField : 감정 결과 저장 (ex. 행복, 슬픔 등)
# # auto_now_add=True : 저장 시 자동으로 현재 시간 저장
from django.db import models

class Product(models.Model):
    # AI 인식용 이름 (예: red_bean_bread)
    category_name = models.CharField(max_length=50, unique=True)
    # 실제 보여질 이름 (예: 단팥빵)
    display_name = models.CharField(max_length=100)
    # 가격 및 재고
    price = models.IntegerField()
    stock = models.IntegerField(default=0)
    
    def __str__(self):
        return self.display_name