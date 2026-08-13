from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, viewsets, generics, permissions
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.exceptions import PermissionDenied 
from django.db.models import F
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

from .models import DiscountProduct, Store, Order, Product
from .serializers import StoreSerializer, DiscountProductSerializer, ProductSerializer
from .detect_views import ShelfScanningView
import re
import os
import requests
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.conf import settings


class BulkProductSaveView(APIView):
    def post(self, request):
        user = request.user
        store = Store.objects.filter(owner=user).first()
        if not store:
            return Response({"error": "가게 정보를 찾을 수 없습니다."}, status=400)

        products_data = request.data.get('products', [])
        saved_count = 0

        for item in products_data:
            product_id = item.get('product') or item.get('product_id')
            if not product_id:
                return Response({"error": "product_id가 없습니다."}, status=400)
            
            orig_price = item.get('price', 0) 
            dis_price = item.get('discount_price', orig_price)

            DiscountProduct.objects.create(
                store=store,
                product_id=product_id,
                discount_price=dis_price,
                original_price=orig_price,
                count=item.get('count', 1),
                is_sold_out=(item.get('count', 1) <= 0),
            )
            saved_count += 1

        return Response({"status": "success", "message": f"{saved_count}개 빵 등록 완료! 🥐"})


# 재고 수량 조절
class UpdateCountView(APIView):
    def post(self, request, pk):
        try:
            product = DiscountProduct.objects.get(pk=pk)
            delta = int(request.data.get('delta', 0))
            product.count = max(0, product.count + delta)
            product.is_sold_out = (product.count == 0)
            product.save()
            return Response({
                "status": "success", 
                "count": product.count, 
                "is_sold_out": product.is_sold_out
                })
        except DiscountProduct.DoesNotExist:
            return Response({"error": "상품을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 할인목록 조회
class DiscountProductListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        store = get_my_store(request.user)
        products = DiscountProduct.objects.filter(store=store).order_by('-created_at')
        data = [{
            "id": p.id,
            "name": p.name,
            "original_price": p.original_price,
            "discount_price": p.discount_price,
            "count": p.count,
            "is_sold_out": p.is_sold_out,
            "created_at": p.created_at.strftime('%Y-%m-%d %H:%M'),
            "lat": p.store.lat if p.store else None,
            "lng": p.store.lng if p.store else None,
            "store_name": p.store.store_name if p.store else "알 수 없는 빵집"
        } for p in products]
        return Response(data)


# 상품 목록 조회 + 상품 등록
class ProductListCreateView(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        store = get_my_store(self.request.user)
        return Product.objects.filter(store=store).order_by('-created_at')

    def perform_create(self, serializer):
        store = get_my_store(self.request.user)
        serializer.save(store=store)


# 상품 상세 조회 + 수정 + 삭제
class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        store = get_my_store(self.request.user)
        return Product.objects.filter(store=store)

def get_my_store(user):
    try:
        return user.store
    except Store.DoesNotExist:
        raise PermissionDenied("사장님 계정만 상품 관리가 가능합니다.")


# 가게 목록 및 등록
class StoreViewSet(viewsets.ModelViewSet):
    serializer_class = StoreSerializer

    def get_queryset(self):
        queryset = Store.objects.all()

        sido = self.request.query_params.get('sido')
        sigg = self.request.query_params.get('sigg')
        dong = self.request.query_params.get('dong')

        # 시/도 필터링
        if sido:
            clean_sido = sido[:2]
            queryset = queryset.filter(store_address__icontains=clean_sido)

        # 시/군/구 필터링
        if sigg:
            clean_sigg = sigg.replace('구', '').replace('시', '').strip() if len(sigg) > 2 else sigg
            clean_sigg = clean_sigg.split()[-1] # 공백이 있을 경우 마지막 단어만 추출
            queryset = queryset.filter(store_address__icontains=clean_sigg)

        # 읍/면/동 필터링 
        if dong:
            clean_dong = re.sub(r'[0-9동가리]', '', dong).strip()
            if clean_dong:
                queryset = queryset.filter(store_address__icontains=clean_dong)

        return queryset


# 할인 상품 목록 및 등록
class DiscountProductViewSet(viewsets.ModelViewSet):
    serializer_class = DiscountProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        store = get_my_store(self.request.user)
        return DiscountProduct.objects.filter(store=store).order_by('-created_at')


# 재고차감 로직
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    user = request.user
    data = request.data
    shop_name = data.get('shop_name')

    if hasattr(user, 'store'):
        if user.store.store_name == shop_name:
            return Response({"error": "사장님은 본인 가게의 상품을 구매할 수 없습니다."}, status=400)
    
    order = Order.objects.create(
        pickup_number=data.get('pickup_number'),
        customer_name=data.get('customer_name', '손님1'),
        shop_name=shop_name,
        items_summary=data.get('items_summary'),
        total_price=data.get('total_price'),
        status=data.get('status', '결제완료'),
        pickup_time=data.get('pickup_time')
    )
    
    # 2. 재고 차감
    cart_items = data.get('cartItems', []) 
    print(f"🛒 차감할 아이템 리스트: {cart_items}")

    for item in cart_items:
        product_id = item.get('id')
        qty = int(item.get('quantity', 0))

        if product_id and qty > 0:
            DiscountProduct.objects.filter(id=product_id).update(count=F('count') - qty)
            
            p = DiscountProduct.objects.filter(id=product_id).first()
            if p and p.count <= 0:
                p.count = 0
                p.is_sold_out = True
                p.save()
            
            print(f"✅ 상품ID {product_id} 업데이트 완료")

    return Response({"message": "주문 완료!", "order_id": order.id}, status=status.HTTP_201_CREATED)


# 알바용의 빵 등록 
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_products(request):
    user = request.user
    store = Store.objects.filter(owner=user).first() 

    if not store:
        return Response({"error": "등록된 가게 정보가 없습니다."}, status=400)

    products_data = request.data.get('products', [])

    for data in products_data:
        product_id = data.get('product') or data.get('product_id')
        if not product_id:
            return Response({"error": "product_id가 없습니다."}, status=400)

        orig_p = data.get('original_price') # 원가
        disc_p = data.get('discount_price') # 할인가

        DiscountProduct.objects.create(
            store=store,
            product_id=product_id,
            discount_price=disc_p,
            original_price=orig_p,
            count=data.get('count', 1),
            is_sold_out=(int(data.get('count', 1)) <= 0)
        )
    return Response({"message": "지도 등록 완료!"})


# 해당 계정의 주문리스트
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_orders(request):
    user_nickname = request.query_params.get('nickname')
    
    if not user_nickname:
        return Response({"error": "닉네임이 필요해요!"}, status=400)

    orders = Order.objects.filter(customer_name=user_nickname).order_by('-created_at')
    
    if not orders.exists():
         print("❌ 이 사용자로 등록된 주문이 하나도 없어요!")

    order_list = []
    for order in orders:
        order_list.append({
            "id": order.id,
            "pickup_number": order.pickup_number, 
            "customer_name": order.customer_name,
            "items_summary": order.items_summary,
            "total_price": order.total_price,
            "status": order.status,
            "shop_name": order.shop_name,
            "created_at": order.created_at.strftime('%Y-%m-%d %H:%M')
        })
    
    return Response(order_list)


# 알바용 전체 주문 목록 조회
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_orders(request):
    store = Store.objects.filter(owner=request.user).first()

    if not store:
        return Response({"error": "등록된 가게 정보가 없습니다."}, status=400)
    
    orders = Order.objects.filter(shop_name=store.store_name).order_by('-created_at')
    
    order_list = []
    for order in orders:
        order_list.append({
            "id": order.id,
            "pickup_number": order.pickup_number, 
            "customer_name": order.customer_name,
            "items_summary": order.items_summary,
            "total_price": order.total_price,
            "status": order.status,
            "shop_name": order.shop_name,
            "created_at": order.created_at.strftime('%Y-%m-%d %H:%M')
        })
    
    return Response(order_list)


@api_view(['POST'])
def complete_order(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
        order.status = "픽업완료" # 상태 변경!
        order.save()
        return Response({"message": "픽업이 완료되었습니다."})
    except Order.DoesNotExist:
        return Response({"error": "주문을 찾을 수 없습니다."}, status=404)


@api_view(['GET'])
def get_order_status(request, order_id):
    try:
        order = Order.objects.get(pickup_number=order_id)
        return Response({"status": order.status})
    except Order.DoesNotExist:
        return Response({"error": "주문 없음"}, status=404)

def test_upload_page(request):
    return render(request, 'test_upload.html')


@api_view(['GET'])
@permission_classes([AllowAny])
def get_sgis_token(request):
    """SGIS 토큰 발급 프록시"""
    service_id = getattr(settings, 'SGIS_SERVICE_ID', os.getenv('SGIS_SERVICE_ID', ''))
    security_key = getattr(settings, 'SGIS_SECURITY_KEY', os.getenv('SGIS_SECURITY_KEY', ''))

    url = "https://sgisapi.kostat.go.kr/OpenAPI3/auth/authentication.json"
    params = {
        "consumer_key": service_id,
        "consumer_secret": security_key
    }
    try:
        response = requests.get(url, params=params, timeout=5)
        return JsonResponse(response.json())
    except Exception as e:
        print(f"❌ SGIS Token Backend Error: {e}")
        return JsonResponse({"errCd": -1, "errMsg": str(e)}, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_sgis_stage(request):
    """SGIS 행정구역 단계 조회 프록시"""
    token = request.GET.get('accessToken')
    cd = request.GET.get('cd', '')
    
    url = "https://sgisapi.kostat.go.kr/OpenAPI3/addr/stage.json"
    params = {"accessToken": token}
    if cd:
        params["cd"] = cd
        
    try:
        response = requests.get(url, params=params, timeout=5)
        return JsonResponse(response.json())
    except Exception as e:
        print(f"❌ SGIS Stage Backend Error: {e}")
        return JsonResponse({"errCd": -1, "errMsg": str(e)}, status=500)
        
User = get_user_model()
