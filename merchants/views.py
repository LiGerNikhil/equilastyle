from datetime import timedelta
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, F, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from merchants.models import Merchant, MerchantWallet
from merchants.permissions import (
    get_merchant_for_user,
    is_super_admin,
    merchant_owner_required,
    role_required,
    user_can_access_merchant,
)
from merchants.services import public_product_queryset
from orders.models import OrderItem
from products.models import Product


def store_home(request, slug):
    """Public merchant storefront."""
    merchant = get_object_or_404(
        Merchant,
        slug=slug,
        status=Merchant.Status.ACTIVE,
        verification_status=Merchant.VerificationStatus.VERIFIED,
    )
    products = (
        public_product_queryset()
        .filter(merchant=merchant)
        .select_related('category', 'brand')
        .prefetch_related('images')[:12]
    )
    context = {
        'merchant': merchant,
        'products': products,
        'page_title': f'{merchant.business_name} | EQUILA STYLE',
        'meta_description': merchant.about_text[:160] if merchant.about_text else f'Shop {merchant.business_name} on EQUILA STYLE.',
    }
    return render(request, 'merchants/store_home.html', context)


def store_products(request, slug):
    merchant = get_object_or_404(
        Merchant,
        slug=slug,
        status=Merchant.Status.ACTIVE,
        verification_status=Merchant.VerificationStatus.VERIFIED,
    )
    products = (
        public_product_queryset()
        .filter(merchant=merchant)
        .select_related('category', 'brand')
        .prefetch_related('images', 'variants')
    )
    search = request.GET.get('search', '').strip()
    if search:
        products = products.filter(name__icontains=search)
    sort = request.GET.get('sort', 'newest')
    if sort == 'price_low':
        products = products.order_by('price')
    elif sort == 'price_high':
        products = products.order_by('-price')
    else:
        products = products.order_by('-created_at')

    paginator = Paginator(products, 12)
    page = paginator.get_page(request.GET.get('page'))
    context = {
        'merchant': merchant,
        'page_obj': page,
        'search_query': search,
        'page_title': f'Products — {merchant.business_name}',
    }
    return render(request, 'merchants/store_products.html', context)


def store_about(request, slug):
    merchant = get_object_or_404(
        Merchant,
        slug=slug,
        status=Merchant.Status.ACTIVE,
        verification_status=Merchant.VerificationStatus.VERIFIED,
    )
    return render(request, 'merchants/store_about.html', {'merchant': merchant})


@login_required
@role_required('merchant', 'merchant_staff', 'super_admin')
@merchant_owner_required
def merchant_dashboard(request, merchant=None):
    """Merchant dashboard analytics overview."""
    if merchant is None and is_super_admin(request.user):
        messages.info(request, 'Select a merchant from admin panel or log in as a merchant.')
        return redirect('admin_panel:dashboard')

    since = timezone.now() - timedelta(days=30)
    items = OrderItem.objects.filter(merchant=merchant).select_related('order', 'product')
    recent_items = items.filter(order__created_at__gte=since)

    stats = {
        'revenue': recent_items.aggregate(
            total=Sum(F('price') * F('quantity'))
        )['total'] or Decimal('0'),
        'orders': recent_items.values('order').distinct().count(),
        'products': Product.objects.filter(merchant=merchant).count(),
        'pending_products': Product.objects.filter(
            merchant=merchant,
            approval_status=Product.ApprovalStatus.PENDING,
        ).count(),
    }
    wallet = MerchantWallet.objects.filter(merchant=merchant).first()
    top_products = (
        recent_items.values('product__name')
        .annotate(qty=Sum('quantity'))
        .order_by('-qty')[:5]
    )

    recent_products = (
        Product.objects.filter(merchant=merchant)
        .select_related('category')
        .prefetch_related('images')
        .order_by('-created_at')[:6]
    )

    context = {
        'merchant': merchant,
        'stats': stats,
        'wallet': wallet,
        'top_products': top_products,
        'recent_orders': items.order_by('-order__created_at')[:8],
        'recent_products': recent_products,
    }
    return render(request, 'merchants/portal_dashboard.html', context)


@login_required
@role_required('merchant', 'merchant_staff', 'super_admin')
@merchant_owner_required
def merchant_orders(request, merchant=None):
    items = (
        OrderItem.objects.filter(merchant=merchant)
        .select_related('order', 'product', 'variant')
        .order_by('-order__created_at')
    )
    status_filter = request.GET.get('status')
    if status_filter:
        items = items.filter(fulfillment_status=status_filter)
    paginator = Paginator(items, 20)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'merchants/portal_orders.html', {
        'merchant': merchant,
        'page_obj': page,
        'fulfillment_choices': OrderItem.FULFILLMENT_STATUS_CHOICES,
    })


@login_required
@role_required('merchant', 'merchant_staff', 'super_admin')
@merchant_owner_required
def merchant_wallet(request, merchant=None):
    wallet = get_object_or_404(MerchantWallet, merchant=merchant)
    transactions = merchant.transactions.all()[:50]
    payouts = merchant.payout_requests.all()[:20]
    return render(
        request,
        'merchants/portal_wallet.html',
        {'merchant': merchant, 'wallet': wallet, 'transactions': transactions, 'payouts': payouts},
    )


@login_required
@require_http_methods(['POST'])
def merchant_order_update_status(request, item_id):
    item = get_object_or_404(OrderItem, pk=item_id)
    if not user_can_access_merchant(request.user, item.merchant):
        return JsonResponse({'success': False, 'detail': 'Forbidden'}, status=403)
    new_status = request.POST.get('fulfillment_status')
    valid = dict(OrderItem.FULFILLMENT_STATUS_CHOICES)
    if new_status not in valid:
        return JsonResponse({'success': False, 'detail': 'Invalid status'}, status=400)
    item.fulfillment_status = new_status
    item.save(update_fields=['fulfillment_status'])
    if new_status == 'delivered' and item.merchant_id:
        from merchants.services import credit_merchant_for_order_item
        credit_merchant_for_order_item(item)
    return JsonResponse({'success': True, 'status': new_status, 'display': valid[new_status]})
