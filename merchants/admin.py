from django.contrib import admin

from merchants.models import (
    Merchant,
    MerchantNotification,
    MerchantStaff,
    MerchantTransaction,
    MerchantWallet,
    PayoutRequest,
    Territory,
)


@admin.register(Territory)
class TerritoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'merchant_limit', 'is_exclusive', 'is_active')
    prepopulated_fields = {'slug': ('name',)}


class MerchantWalletInline(admin.StackedInline):
    model = MerchantWallet
    extra = 0


@admin.register(Merchant)
class MerchantAdmin(admin.ModelAdmin):
    list_display = ('merchant_id', 'business_name', 'status', 'verification_status', 'territory', 'joined_at')
    list_filter = ('status', 'verification_status', 'franchise_type')
    search_fields = ('business_name', 'merchant_id', 'email')
    prepopulated_fields = {'slug': ('business_name',)}
    inlines = [MerchantWalletInline]


@admin.register(MerchantStaff)
class MerchantStaffAdmin(admin.ModelAdmin):
    list_display = ('user', 'merchant', 'role', 'is_active')


@admin.register(MerchantTransaction)
class MerchantTransactionAdmin(admin.ModelAdmin):
    list_display = ('merchant', 'transaction_type', 'amount', 'status', 'created_at')
    list_filter = ('transaction_type', 'status')


@admin.register(PayoutRequest)
class PayoutRequestAdmin(admin.ModelAdmin):
    list_display = ('merchant', 'amount', 'status', 'created_at')
    list_filter = ('status',)


@admin.register(MerchantNotification)
class MerchantNotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'recipient', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read')
