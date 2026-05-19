"""
Merchant portal: product list, create, edit, delete.
Products submit for admin approval before appearing on the public shop.
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import F, Sum
from django.forms import inlineformset_factory
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from admin_panel.forms import (
    ProductImageForm,
    ProductVariantForm,
    RequiredAtLeastOneInlineFormSet,
)
from admin_panel.models import Notification
from merchants.permissions import (
    can_manage_merchant_products,
    get_merchant_for_user,
    is_super_admin,
    merchant_owner_required,
    role_required,
)
from merchants.product_forms import MerchantProductForm
from merchants.services import notify_user
from products.models import Category, Product, ProductImage, ProductVariant


def _merchant_product_queryset(merchant):
    return (
        Product.objects.filter(merchant=merchant)
        .select_related('category')
        .prefetch_related('images', 'variants')
    )


def _get_merchant_product(merchant, product_id):
    return get_object_or_404(_merchant_product_queryset(merchant), pk=product_id)


def _apply_merchant_product_meta(product, *, merchant, user, save_as_draft=False):
    product.merchant = merchant
    product.published_by = user
    if save_as_draft:
        product.approval_status = Product.ApprovalStatus.DRAFT
        product.is_available = False
        product.is_active = False
    else:
        product.approval_status = Product.ApprovalStatus.PENDING
        product.is_available = False
        product.is_active = False
    product.rejection_reason = ''
    return product


def _notify_product_submitted(product):
    Notification.objects.create(
        title='Product pending approval',
        message=f'"{product.name}" from {product.merchant.business_name} needs review.',
        notification_type='product_approval',
        product_id=product.pk,
    )
    if product.published_by_id:
        notify_user(
            recipient=product.published_by,
            merchant=product.merchant,
            notification_type='product_approval',
            title='Product submitted',
            message=f'"{product.name}" was sent for admin approval. You will be notified when it is live.',
        )


def _product_formsets(product, data=None, files=None, *, extra_variants=1):
    VariantFormSet = inlineformset_factory(
        Product,
        ProductVariant,
        form=ProductVariantForm,
        formset=RequiredAtLeastOneInlineFormSet,
        extra=extra_variants,
        can_delete=True,
    )
    ImageFormSet = inlineformset_factory(
        Product,
        ProductImage,
        form=ProductImageForm,
        extra=1,
        can_delete=True,
    )
    if data is not None:
        return (
            VariantFormSet(data, instance=product, prefix='variants'),
            ImageFormSet(data, files, instance=product, prefix='images'),
        )
    return (
        VariantFormSet(instance=product, prefix='variants'),
        ImageFormSet(instance=product, prefix='images'),
    )


def _check_product_access(request, merchant):
    if not can_manage_merchant_products(request.user):
        raise PermissionDenied('You do not have permission to manage products.')


@login_required
@role_required('merchant', 'merchant_staff', 'super_admin')
@merchant_owner_required
def merchant_product_size_options(request, merchant=None):
    _check_product_access(request, merchant)
    category_id = request.GET.get('category_id')
    if not category_id:
        return JsonResponse({'sizes': None})
    category = get_object_or_404(Category, pk=category_id)
    allowed = ProductVariant.allowed_sizes_for_category(getattr(category, 'name', ''))
    return JsonResponse({'sizes': allowed})


@login_required
@role_required('merchant', 'merchant_staff', 'super_admin')
@merchant_owner_required
def merchant_products(request, merchant=None):
    _check_product_access(request, merchant)
    products = _merchant_product_queryset(merchant).order_by('-created_at')

    status_filter = request.GET.get('status', '')
    search = request.GET.get('search', '').strip()
    if status_filter:
        products = products.filter(approval_status=status_filter)
    if search:
        products = products.filter(name__icontains=search)

    from django.core.paginator import Paginator
    paginator = Paginator(products, 15)
    page = paginator.get_page(request.GET.get('page'))

    counts = {
        'all': Product.objects.filter(merchant=merchant).count(),
        'approved': Product.objects.filter(merchant=merchant, approval_status='approved').count(),
        'pending': Product.objects.filter(merchant=merchant, approval_status='pending').count(),
        'draft': Product.objects.filter(merchant=merchant, approval_status='draft').count(),
        'rejected': Product.objects.filter(merchant=merchant, approval_status='rejected').count(),
    }

    return render(request, 'merchants/products.html', {
        'merchant': merchant,
        'page_obj': page,
        'search_query': search,
        'status_filter': status_filter,
        'counts': counts,
        'approval_choices': Product.ApprovalStatus.choices,
    })


@login_required
@role_required('merchant', 'merchant_staff', 'super_admin')
@merchant_owner_required
def merchant_product_create(request, merchant=None):
    _check_product_access(request, merchant)
    product = Product()
    save_as_draft = False

    if request.method == 'POST':
        save_as_draft = request.POST.get('action') == 'draft'
        form = MerchantProductForm(request.POST, instance=product)
        variant_formset, image_formset = _product_formsets(product, request.POST, request.FILES)

        if form.is_valid() and variant_formset.is_valid() and image_formset.is_valid():
            product = form.save(commit=False)
            _apply_merchant_product_meta(
                product, merchant=merchant, user=request.user, save_as_draft=save_as_draft,
            )
            product.save()
            variant_formset.instance = product
            image_formset.instance = product
            variant_formset.save()
            image_formset.save()
            product.refresh_availability_from_variants(save=True)

            if not save_as_draft:
                _notify_product_submitted(product)
                messages.success(request, 'Product submitted for approval. It will appear on the shop once approved.')
            else:
                messages.success(request, 'Product saved as draft.')
            return redirect('merchants:products')
    else:
        form = MerchantProductForm(instance=product)
        variant_formset, image_formset = _product_formsets(product)

    return render(request, 'merchants/product_form.html', {
        'merchant': merchant,
        'form': form,
        'variant_formset': variant_formset,
        'image_formset': image_formset,
        'mode': 'create',
        'product': product,
    })


@login_required
@role_required('merchant', 'merchant_staff', 'super_admin')
@merchant_owner_required
def merchant_product_edit(request, product_id, merchant=None):
    _check_product_access(request, merchant)
    product = _get_merchant_product(merchant, product_id)
    save_as_draft = False

    if request.method == 'POST':
        save_as_draft = request.POST.get('action') == 'draft'
        form = MerchantProductForm(request.POST, instance=product)
        variant_formset, image_formset = _product_formsets(
            product, request.POST, request.FILES, extra_variants=0,
        )

        if form.is_valid() and variant_formset.is_valid() and image_formset.is_valid():
            product = form.save(commit=False)
            was_approved = product.approval_status == Product.ApprovalStatus.APPROVED
            _apply_merchant_product_meta(
                product, merchant=merchant, user=request.user, save_as_draft=save_as_draft,
            )
            product.save()
            variant_formset.save()
            image_formset.save()
            product.refresh_availability_from_variants(save=True)

            if not save_as_draft:
                if was_approved:
                    messages.info(request, 'Approved product updated — sent back for admin re-approval.')
                _notify_product_submitted(product)
                messages.success(request, 'Product submitted for approval.')
            else:
                messages.success(request, 'Draft saved.')
            return redirect('merchants:products')
    else:
        form = MerchantProductForm(instance=product)
        variant_formset, image_formset = _product_formsets(product, extra_variants=0)

    return render(request, 'merchants/product_form.html', {
        'merchant': merchant,
        'form': form,
        'variant_formset': variant_formset,
        'image_formset': image_formset,
        'mode': 'edit',
        'product': product,
    })


@login_required
@require_http_methods(['POST'])
def merchant_product_delete(request, product_id):
    merchant = get_merchant_for_user(request.user)
    if merchant is None and not is_super_admin(request.user):
        return JsonResponse({'success': False, 'detail': 'Forbidden'}, status=403)
    if not can_manage_merchant_products(request.user):
        return JsonResponse({'success': False, 'detail': 'Forbidden'}, status=403)

    if is_super_admin(request.user) and merchant is None:
        product = get_object_or_404(Product, pk=product_id)
    else:
        product = _get_merchant_product(merchant, product_id)

    name = product.name
    product.delete()
    messages.success(request, f'Product "{name}" deleted.')
    return JsonResponse({'success': True, 'message': f'"{name}" deleted.'})
