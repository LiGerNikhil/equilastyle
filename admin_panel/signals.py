from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from orders.models import Order
from .models import Notification


@receiver(post_save, sender=Order)
def create_order_notification(sender, instance, created, **kwargs):
    """
    Create notification when a new order is created
    """
    if created:
        # Get order items details
        items_details = []
        for item in instance.items.all():
            size_info = f" (Size: {item.variant.size})" if item.variant else ""
            items_details.append(f"{item.quantity}x {item.product.name}{size_info}")
        
        items_text = ", ".join(items_details[:3])  # Show first 3 items
        if instance.items.count() > 3:
            items_text += f" and {instance.items.count() - 3} more items"
        
        # Create notification for new order
        Notification.objects.create(
            title=f'New Order #{instance.id}',
            message=f'Order from {instance.user.get_full_name() or instance.user.username} - ${instance.total_price} - {items_text}',
            notification_type='order',
            user=instance.user,
            order_id=instance.id
        )


@receiver(post_save, sender=User)
def create_user_notification(sender, instance, created, **kwargs):
    """
    Create notification when a new user registers
    """
    if created:
        # Create notification for new user registration
        Notification.objects.create(
            title=f'New User Registration',
            message=f'User {instance.get_full_name() or instance.username} has registered',
            notification_type='user',
            user=instance
        )
