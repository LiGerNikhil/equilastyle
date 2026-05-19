"""
Multi-merchant / franchise domain models.

Architecture: HQ-owned products have merchant=NULL; franchise products link to Merchant.
Commission and payouts flow through MerchantWallet + MerchantTransaction.
"""
from decimal import Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class Territory(models.Model):
    """Geographic franchise territory (e.g. Delhi NCR, Mumbai)."""

    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True)
    description = models.TextField(blank=True)
    merchant_limit = models.PositiveIntegerField(
        default=0,
        help_text='0 = unlimited merchants in this territory.',
    )
    is_exclusive = models.BooleanField(
        default=False,
        help_text='If True, only one active merchant allowed (when limit=1).',
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'territories'
        indexes = [
            models.Index(fields=['is_active', 'slug']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:140] or 'territory'
        super().save(*args, **kwargs)

    @property
    def active_merchant_count(self):
        return self.merchants.filter(status=Merchant.Status.ACTIVE).count()

    def can_add_merchant(self):
        if not self.is_active:
            return False
        if self.merchant_limit == 0:
            return True
        return self.active_merchant_count < self.merchant_limit


class Merchant(models.Model):
    """Franchise / multi-merchant store entity."""

    class FranchiseType(models.TextChoices):
        FRANCHISE = 'franchise', 'Franchise'
        PARTNER = 'partner', 'Partner Store'
        FLAGSHIP = 'flagship', 'Flagship'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        ACTIVE = 'active', 'Active'
        SUSPENDED = 'suspended', 'Suspended'
        INACTIVE = 'inactive', 'Inactive'

    class VerificationStatus(models.TextChoices):
        PENDING = 'pending', 'Pending Verification'
        VERIFIED = 'verified', 'Verified'
        REJECTED = 'rejected', 'Rejected'

    # Readable ID e.g. EQ-M-00001
    merchant_id = models.CharField(max_length=20, unique=True, editable=False)
    slug = models.SlugField(max_length=160, unique=True)
    business_name = models.CharField(max_length=200)
    owner_name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    gst_number = models.CharField(max_length=20, blank=True)
    franchise_type = models.CharField(
        max_length=20,
        choices=FranchiseType.choices,
        default=FranchiseType.FRANCHISE,
    )
    commission_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('10.00'),
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('100'))],
        help_text='Platform commission percentage retained from merchant sales.',
    )
    territory = models.ForeignKey(
        Territory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='merchants',
    )
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default='India')
    pincode = models.CharField(max_length=12)
    logo = models.ImageField(upload_to='merchants/logos/', blank=True, null=True)
    banner = models.ImageField(upload_to='merchants/banners/', blank=True, null=True)
    store_policy = models.TextField(blank=True)
    about_text = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    verification_status = models.CharField(
        max_length=20,
        choices=VerificationStatus.choices,
        default=VerificationStatus.PENDING,
    )
    # Link to primary merchant owner account (optional until onboarding)
    owner_user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='owned_merchant',
    )
    regional_manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_merchants',
    )
    joined_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-joined_at']
        indexes = [
            models.Index(fields=['status', 'verification_status']),
            models.Index(fields=['slug']),
            models.Index(fields=['merchant_id']),
            models.Index(fields=['territory', 'status']),
        ]

    def __str__(self):
        return f'{self.business_name} ({self.merchant_id})'

    def save(self, *args, **kwargs):
        if not self.merchant_id:
            self.merchant_id = self._generate_merchant_id()
        if not self.slug:
            self.slug = self._generate_unique_slug()
        super().save(*args, **kwargs)

    def _generate_merchant_id(self):
        last = (
            Merchant.objects.order_by('-id')
            .values_list('id', flat=True)
            .first()
        )
        seq = (last or 0) + 1
        return f'EQ-M-{seq:05d}'

    def _generate_unique_slug(self):
        base = slugify(self.business_name)[:120] or 'store'
        slug = base
        i = 2
        while Merchant.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f'{base}-{i}'[:160]
            i += 1
        return slug

    @property
    def is_public(self):
        return (
            self.status == self.Status.ACTIVE
            and self.verification_status == self.VerificationStatus.VERIFIED
        )


class MerchantStaff(models.Model):
    """Staff account scoped to a single merchant with granular permissions."""

    class PermissionRole(models.TextChoices):
        PRODUCT_MANAGER = 'product_manager', 'Product Manager'
        INVENTORY_MANAGER = 'inventory_manager', 'Inventory Manager'
        ORDER_MANAGER = 'order_manager', 'Order Manager'
        SUPPORT = 'support', 'Support Staff'

    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, related_name='staff_members')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='merchant_staff_roles',
    )
    role = models.CharField(max_length=30, choices=PermissionRole.choices)
    can_manage_products = models.BooleanField(default=False)
    can_manage_inventory = models.BooleanField(default=False)
    can_manage_orders = models.BooleanField(default=False)
    can_view_analytics = models.BooleanField(default=False)
    can_manage_coupons = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('merchant', 'user')]
        indexes = [
            models.Index(fields=['merchant', 'is_active']),
        ]

    def __str__(self):
        return f'{self.user.email} @ {self.merchant.business_name}'


class MerchantWallet(models.Model):
    """Merchant balance ledger (pending vs withdrawable)."""

    merchant = models.OneToOneField(Merchant, on_delete=models.CASCADE, related_name='wallet')
    pending_balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    withdrawable_balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_earned = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    total_withdrawn = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Wallet {self.merchant.merchant_id}'


class MerchantTransaction(models.Model):
    """Immutable ledger entries for commissions, payouts, adjustments."""

    class TransactionType(models.TextChoices):
        SALE_CREDIT = 'sale_credit', 'Sale Credit'
        COMMISSION_DEBIT = 'commission_debit', 'Platform Commission'
        PAYOUT = 'payout', 'Payout'
        REFUND = 'refund', 'Refund'
        ADJUSTMENT = 'adjustment', 'Adjustment'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'

    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, related_name='transactions')
    order_item = models.ForeignKey(
        'orders.OrderItem',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='merchant_transactions',
    )
    transaction_type = models.CharField(max_length=30, choices=TransactionType.choices)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    commission_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    net_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    reference = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['merchant', '-created_at']),
            models.Index(fields=['status', 'transaction_type']),
        ]

    def __str__(self):
        return f'{self.transaction_type} {self.amount} ({self.merchant.merchant_id})'


class PayoutRequest(models.Model):
    """Merchant withdrawal request — ready for Razorpay Route / Stripe Connect."""

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        PROCESSING = 'processing', 'Processing'
        PAID = 'paid', 'Paid'
        REJECTED = 'rejected', 'Rejected'

    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, related_name='payout_requests')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    payment_reference = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_payouts',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['merchant', 'status']),
        ]

    def __str__(self):
        return f'Payout {self.amount} — {self.merchant.merchant_id}'


class MerchantNotification(models.Model):
    """In-app notifications for merchants and platform staff."""

    class NotificationType(models.TextChoices):
        PRODUCT_APPROVAL = 'product_approval', 'Product Approval'
        PRODUCT_REJECTION = 'product_rejection', 'Product Rejection'
        NEW_ORDER = 'new_order', 'New Order'
        PAYOUT_UPDATE = 'payout_update', 'Payout Update'
        LOW_INVENTORY = 'low_inventory', 'Low Inventory'
        VERIFICATION = 'verification', 'Merchant Verification'
        SYSTEM = 'system', 'System'

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='merchant_notifications',
    )
    merchant = models.ForeignKey(
        Merchant,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications',
    )
    notification_type = models.CharField(max_length=30, choices=NotificationType.choices)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    send_email = models.BooleanField(default=False)
    email_sent = models.BooleanField(default=False)
    metadata = models.TextField(blank=True, default='{}')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read', '-created_at']),
        ]

    def __str__(self):
        return self.title
