from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ShelfScanningView, BulkProductSaveView, DiscountProductListView, 
    UpdateCountView, StoreViewSet, DiscountProductViewSet, 
    ProductListCreateView, ProductDetailView,
    login_view, signup_view
)
from . import views

router = DefaultRouter()
router.register(r'stores', StoreViewSet, basename='store')
router.register(r'discounts', DiscountProductViewSet, basename='discountproduct')

urlpatterns = [
    path('detect/', ShelfScanningView.as_view(), name='detect'),
    path('api/detect/', ShelfScanningView.as_view(), name='shelf_scanning'),
    path('', include(router.urls)),
    path('save-products/', BulkProductSaveView.as_view(), name='save_products'),
    path('list/', DiscountProductListView.as_view(), name='product_list'),
    path('update-count/<int:pk>/', UpdateCountView.as_view(), name='update_count'),
    path('api/', include(router.urls)),
    path('api/create-order/', views.create_order),
    path('api/my-orders/', views.get_my_orders),
    path('api/get-orders/', views.get_orders),
    path('api/complete-order/<int:order_id>/', views.complete_order),
    path('api/order-status/<int:order_id>/', views.get_order_status),
    path('products/', ProductListCreateView.as_view(), name='product-list-create'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('api/auth/login/', login_view, name='login'),
    path('api/auth/signup/', signup_view, name='signup'),
    
]