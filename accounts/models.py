from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # 역할 구분 (사장님 vs 손님)
    is_owner = models.BooleanField(default=False)
    # 공통 정보 (핸드폰번호)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    
    # 사장님 전용 필드
    # 사업자 번호 (10자리 또는 12자리 등)
    business_number = models.CharField(max_length=12, blank=True, null=True, unique=True)
    # 가게 이름
    store_name = models.CharField(max_length=50, blank=True, null=True)
    # 가게 주소
    store_address = models.CharField(max_length=255, blank=True, null=True)
    # 승인 상태 (사장님은 관리자가 확인 후 승인해주는 로직을 대비)
    is_approved = models.BooleanField(default=False)

    # 손님 전용 필드
    nickname = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        role = "사장님" if self.is_owner else "손님"
        return f"[{role}] {self.username}"