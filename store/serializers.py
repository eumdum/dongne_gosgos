from rest_framework import serializers
from .models import Store, Product, DiscountProduct, Order

# 빵 사전
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id',
            'display_name',     # 서비스 화면에 보이는 이름
            'normalized_name',  # ocr 정규화 이름
            'category_name',    # ai카테고리 분류 이름
            'price',
            'image',
            'label_image',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'store', 'normalized_name', 'created_at', 'updated_at']

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user

        # 로그인된 사장님의 store 자동 연결
        store = user.store
        validated_data['store'] = store
        return super().create(validated_data)

# 세일 중인 상품 정보
class DiscountProductSerializer(serializers.ModelSerializer):
    display_name = serializers.CharField(source='product.display_name', read_only=True)

    class Meta:
        model = DiscountProduct
        fields = [
            'id',
            'display_name',
            'original_price',
            'discount_price',
            'count',
            'is_sold_out',
            'created_at',
            'store',
            'product',
        ]

# 가게 정보 
class StoreSerializer(serializers.ModelSerializer):
    discounts = DiscountProductSerializer(many=True, read_only=True)
    class Meta:
        model = Store
        fields = [
            'id', 'store_name', 'store_address', 'lat', 'lng', 'owner',
            'discounts', 'created_at'
        ]

# 구매이력
class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'id', 'pickup_number', 'customer_name', 'shop_name', 
            'items_summary', 'total_price', 'status', 'pickup_time', 'created_at'
        ]