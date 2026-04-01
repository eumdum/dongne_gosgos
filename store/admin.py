from django.contrib import admin
from .models import DiscountProduct, Store, Product, Order

class ProductInline(admin.TabularInline):
    model = Product
    extra = 1 

class DiscountProductInline(admin.TabularInline):
    model = DiscountProduct
    extra = 1

@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('store_name', 'store_address', 'lat', 'lng', 'owner')
    inlines = [ProductInline, DiscountProductInline]

admin.site.register(DiscountProduct)
admin.site.register(Product)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['customer_name', 'pickup_number', 'items_summary', 'total_price', 'status', 'created_at']
    fields = ['customer_name', 'status'] 
    list_editable = ['status']