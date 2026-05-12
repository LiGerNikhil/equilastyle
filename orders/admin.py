from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['get_total_price']
    
    def get_total_price(self, obj):
        return f"${obj.get_total_price():.2f}"
    get_total_price.short_description = 'Total Price'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'status', 'payment_method', 'payment_status', 'total_price', 'created_at']
    list_filter = ['status', 'payment_method', 'payment_status', 'created_at']
    search_fields = ['order_number', 'user__email', 'razorpay_order_id', 'razorpay_payment_id']
    readonly_fields = ['order_number', 'created_at', 'updated_at', 'razorpay_order_id', 'razorpay_payment_id']
    inlines = [OrderItemInline]
    fieldsets = (
        ('Order Info', {
            'fields': ('order_number', 'user', 'status', 'total_price')
        }),
        ('Shipping & Billing', {
            'fields': ('shipping_address', 'billing_address', 'phone_number', 'email')
        }),
        ('Payment Details', {
            'fields': ('payment_method', 'payment_status', 'razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature')
        }),
        ('Additional Info', {
            'fields': ('notes', 'created_at', 'updated_at')
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'variant', 'quantity', 'price', 'get_total_price']
    list_filter = ['order__created_at']
    search_fields = ['product__name', 'order__order_number']
    readonly_fields = ['get_total_price']
    
    def get_total_price(self, obj):
        return f"${obj.get_total_price():.2f}"
    get_total_price.short_description = 'Total Price'
