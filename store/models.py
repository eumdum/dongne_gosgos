from ast import mod
from email.policy import default
from tabnanny import verbose
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator

class Store(models.Model):
    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, 
        related_name='store', 
        null=True, 
        blank=True
        )
    
    store_name = models.CharField(max_length=100, verbose_name="가게명")
    store_address = models.CharField(max_length=255, verbose_name="상세주소")
    
    lat = models.FloatField(verbose_name="위도", null=True, blank=True)
    lng = models.FloatField(verbose_name="경도", null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.store_name

# 빵 사전
class Product(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='products')
    category_name = models.CharField(max_length=100, blank=True, verbose_name="AI 카테고리명")
    display_name = models.CharField(max_length=100, verbose_name="상품명")
    normalized_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="정규화 상품명"
    )
    price = models.IntegerField(validators=[MinValueValidator(0)], verbose_name="정가")
    
    image = models.ImageField(
        upload_to='products/images/',
        null=True,
        blank=True,
        verbose_name="대표 사진"
    )

    label_image = models.ImageField(
        upload_to='products/label_images/',
        null=True,
        blank=True,
        verbose_name="빵+네임택 사진"
    )

    description = models.TextField(
        null=True,
        blank=True,
        verbose_name="설명"
    )

    # 판매 여부
    is_active = models.BooleanField(default=True, verbose_name="사용 여부")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('store', 'display_name')

    def __str__(self):
        return f"[{self.store.store_name}] {self.display_name}"

    def save(self, *args, **kwargs):
        self.normalized_name = self.normalize_name(self.display_name)
        super().save(*args, **kwargs)

    @staticmethod
    def normalize_name(name):
        if not name:
            return ""
        import re
        name = str(name).replace(" ", "")
        name = re.sub(r'[^가-힣0-9]', '', name)
        return name.strip()

# 할인하는 상품에 대한 정보
class DiscountProduct(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='discounts')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='discount_items')
    original_price = models.PositiveIntegerField(verbose_name="원가")
    discount_price = models.PositiveIntegerField(verbose_name="할인가")

    count = models.PositiveIntegerField(default=1, validators=[MinValueValidator(0)], verbose_name="수량")
    is_sold_out = models.BooleanField(default=False, verbose_name="품절 여부")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.store.store_name} - {self.product.display_name} (할인중)"

    @property
    def name(self):
        return self.product.display_name

    def save(self, *args, **kwargs):
        if self.count == 0:
            self.is_sold_out = True

        if not self.original_price and self.product_id:
            self.original_price = self.product.price

        super().save(*args, **kwargs)


class Order(models.Model):
    STATUS_CHOICES = [
        ('결제완료', '결제완료'),
        ('대기중', '대기중'),
        ('픽업완료', '픽업완료'),
        ('취소', '취소'),
    ]

    customer_name = models.CharField(max_length=50, default="손님1")
    shop_name = models.CharField(max_length=100)
    pickup_number = models.IntegerField(null=True)
    items_summary = models.TextField()
    total_price = models.IntegerField()

    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES,
        default="결제완료"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    pickup_time = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.customer_name} - {self.shop_name} ({self.created_at.strftime('%m/%d %H:%M')})"