"""
Business logic: commissions, notifications, product visibility.
"""
from decimal import Decimal

from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Q

from products.models import Product


def public_product_queryset():
    """
    Products visible on the public storefront.
    HQ products (no merchant) need approval; merchant products need active+verified merchant.
    """
    return Product.objects.filter(
        is_available=True,
        approval_status=Product.ApprovalStatus.APPROVED,
    ).filter(
        Q(merchant__isnull=True)
        | Q(
            merchant__status='active',
            merchant__verification_status='verified',
        )
    )


def notify_user(*, recipient, notification_type, title, message, merchant=None, send_email=False, metadata=None):
    import json

    from merchants.models import MerchantNotification

    notification = MerchantNotification.objects.create(
        recipient=recipient,
        merchant=merchant,
        notification_type=notification_type,
        title=title,
        message=message,
        send_email=send_email,
        metadata=json.dumps(metadata or {}),
    )
    if send_email and recipient.email:
        try:
            send_mail(
                subject=title,
                message=message,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@equilastyle.com'),
                recipient_list=[recipient.email],
                fail_silently=True,
            )
            notification.email_sent = True
            notification.save(update_fields=['email_sent'])
        except Exception:
            pass
    return notification


@transaction.atomic
def credit_merchant_for_order_item(order_item):
    """
    Calculate platform commission and credit merchant wallet when item is delivered.
    Idempotent: skips if a completed sale_credit already exists for this item.
    """
    from merchants.models import Merchant, MerchantTransaction, MerchantWallet

    if not order_item.merchant_id:
        return None

    if order_item.merchant_transactions.filter(
        transaction_type=MerchantTransaction.TransactionType.SALE_CREDIT,
        status=MerchantTransaction.Status.COMPLETED,
    ).exists():
        return None

    merchant = order_item.merchant
    gross = order_item.get_total_price()
    rate = merchant.commission_rate / Decimal('100')
    commission = (gross * rate).quantize(Decimal('0.01'))
    net = gross - commission

    wallet, _ = MerchantWallet.objects.select_for_update().get_or_create(merchant=merchant)

    MerchantTransaction.objects.create(
        merchant=merchant,
        order_item=order_item,
        transaction_type=MerchantTransaction.TransactionType.SALE_CREDIT,
        amount=gross,
        commission_amount=commission,
        net_amount=net,
        status=MerchantTransaction.Status.COMPLETED,
        reference=f'order-item-{order_item.pk}',
        notes='Sale credited on delivery',
    )
    MerchantTransaction.objects.create(
        merchant=merchant,
        order_item=order_item,
        transaction_type=MerchantTransaction.TransactionType.COMMISSION_DEBIT,
        amount=commission,
        commission_amount=commission,
        net_amount=-commission,
        status=MerchantTransaction.Status.COMPLETED,
        reference=f'commission-{order_item.pk}',
    )

    wallet.pending_balance += net
    wallet.total_earned += net
    wallet.save(update_fields=['pending_balance', 'total_earned', 'updated_at'])

    order_item.payout_status = 'credited'
    order_item.save(update_fields=['payout_status'])

    if merchant.owner_user_id:
        notify_user(
            recipient=merchant.owner_user,
            merchant=merchant,
            notification_type='payout_update',
            title='Earnings credited',
            message=f'₹{net} credited to your wallet for order item #{order_item.pk}.',
            send_email=False,
        )
    return net
