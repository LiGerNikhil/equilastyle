from django.contrib import admin
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['created_at']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'updated_at', 'get_total_items', 'get_total_price']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [CartItemInline]
    
    def get_total_items(self, obj):
        return obj.get_total_items()
    get_total_items.short_description = 'Total Items'
    
    def get_total_price(self, obj):
        return f"${obj.get_total_price():.2f}"
    get_total_price.short_description = 'Total Price'


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'product', 'variant', 'quantity', 'get_total_price', 'created_at']
    list_filter = ['created_at']
    search_fields = ['product__name', 'cart__user__email']
    readonly_fields = ['created_at']
    
    def get_total_price(self, obj):
        return f"${obj.get_total_price():.2f}"
    get_total_price.short_description = 'Total Price'
