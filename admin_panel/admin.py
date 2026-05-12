from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin configuration for Notification model"""
    
    list_display = ('title', 'notification_type', 'is_read', 'created_at', 'user')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('title', 'message', 'user__username', 'user__email')
    list_editable = ('is_read',)
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Notification Details', {
            'fields': ('title', 'message', 'notification_type', 'is_read')
        }),
        ('References', {
            'fields': ('user', 'order_id', 'product_id'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with related objects"""
        return super().get_queryset(request).select_related('user')
    
    def has_add_permission(self, request):
        """Disable manual addition of notifications"""
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        """Allow staff to mark as read but not modify other fields"""
        if obj and not request.user.is_superuser:
            return False
        return super().has_change_permission(request, obj)
    
    def has_delete_permission(self, request, obj=None):
        """Only superusers can delete notifications"""
        return request.user.is_superuser
    
    actions = ['mark_as_read', 'mark_as_unread', 'delete_old_notifications']
    
    def mark_as_read(self, request, queryset):
        """Mark selected notifications as read"""
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} notifications marked as read.')
    mark_as_read.short_description = 'Mark selected notifications as read'
    
    def mark_as_unread(self, request, queryset):
        """Mark selected notifications as unread"""
        updated = queryset.update(is_read=False)
        self.message_user(request, f'{updated} notifications marked as unread.')
    mark_as_unread.short_description = 'Mark selected notifications as unread'
    
    def delete_old_notifications(self, request, queryset):
        """Delete notifications older than 30 days"""
        from django.utils import timezone
        from datetime import timedelta
        
        cutoff_date = timezone.now() - timedelta(days=30)
        deleted_count, _ = Notification.objects.filter(created_at__lt=cutoff_date).delete()
        self.message_user(request, f'Deleted {deleted_count} old notifications.')
    delete_old_notifications.short_description = 'Delete notifications older than 30 days'
