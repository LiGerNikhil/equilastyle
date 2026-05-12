from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Count, Avg, Sum
from django.utils import timezone
from datetime import datetime, timedelta
import time
from django.contrib import messages
from django.forms import inlineformset_factory
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
import json
from accounts.models import User
from orders.models import Order, OrderItem
from products.models import Product, ProductVariant, ProductImage
from blog.models import Post
from blog.forms import PostCreateForm

from .forms import ProductForm, ProductImageForm, ProductVariantForm, RequiredAtLeastOneInlineFormSet
from .models import Notification

def is_staff_user(user):
    return user.is_authenticated and user.is_staff


@login_required
@user_passes_test(is_staff_user, login_url='accounts:login')
def admin_dashboard(request):
    """Admin dashboard home page with overview statistics"""
    
    # Get statistics
    total_users = User.objects.count()
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    total_posts = Post.objects.count()
    
    # Recent orders
    recent_orders = Order.objects.order_by('-created_at')[:10]
    
    # Recent users
    recent_users = User.objects.order_by('-date_joined')[:10]
    
    # Sales data (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_orders_count = Order.objects.filter(created_at__gte=thirty_days_ago).count()
    
    context = {
        'total_users': total_users,
        'total_products': total_products,
        'total_orders': total_orders,
        'total_posts': total_posts,
        'recent_orders': recent_orders,
        'recent_users': recent_users,
        'recent_orders_count': recent_orders_count,
    }
    
    return render(request, 'admin/dashboard.html', context)


@login_required
@user_passes_test(is_staff_user, login_url='accounts:login')
def admin_users(request):
    """Admin users management page"""
    
    users = User.objects.all().order_by('-date_joined')
    
    # Filter by search
    search_query = request.GET.get('search', '')
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    context = {
        'users': users,
        'search_query': search_query,
    }
    
    return render(request, 'admin/users.html', context)


@login_required
@user_passes_test(is_staff_user, login_url='accounts:login')
def admin_products(request):
    """Admin products management page"""

    products = (
        Product.objects.select_related('category', 'brand')
        .prefetch_related('images', 'variants')
        .all()
        .order_by('-created_at')
    )
    
    # Filter by search
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(brand__name__icontains=search_query)
        )
    
    context = {
        'products': products,
        'search_query': search_query,
    }
    
    return render(request, 'admin/products.html', context)


@login_required
@user_passes_test(is_staff_user, login_url='accounts:login')
def admin_product_size_options(request):
    category_id = request.GET.get('category_id')
    if not category_id:
        return JsonResponse({'sizes': None}, status=200)

    category = get_object_or_404(Category, pk=category_id)
    allowed = ProductVariant.allowed_sizes_for_category(getattr(category, 'name', ''))
    return JsonResponse({'sizes': allowed}, status=200)


@login_required
@user_passes_test(is_staff_user, login_url='accounts:login')
def admin_product_create(request):
    VariantFormSet = inlineformset_factory(
        Product,
        ProductVariant,
        form=ProductVariantForm,
        formset=RequiredAtLeastOneInlineFormSet,
        extra=1,
        can_delete=True,
    )
    ImageFormSet = inlineformset_factory(
        Product,
        ProductImage,
        form=ProductImageForm,
        extra=1,
        can_delete=True,
    )

    product = Product()

    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        variant_formset = VariantFormSet(request.POST, instance=product, prefix='variants')
        image_formset = ImageFormSet(request.POST, request.FILES, instance=product, prefix='images')

        if form.is_valid() and variant_formset.is_valid() and image_formset.is_valid():
            product = form.save()
            variant_formset.instance = product
            image_formset.instance = product
            variant_formset.save()
            image_formset.save()

            product.refresh_availability_from_variants(save=True)
            messages.success(request, 'Product created successfully.')
            return redirect('admin_panel:products')
    else:
        form = ProductForm(instance=product)
        variant_formset = VariantFormSet(instance=product, prefix='variants')
        image_formset = ImageFormSet(instance=product, prefix='images')

    context = {
        'form': form,
        'variant_formset': variant_formset,
        'image_formset': image_formset,
        'mode': 'create',
        'product': product,
    }
    return render(request, 'admin/product_form.html', context)


@login_required
@user_passes_test(is_staff_user, login_url='accounts:login')
def admin_product_edit(request, product_id: int):
    VariantFormSet = inlineformset_factory(
        Product,
        ProductVariant,
        form=ProductVariantForm,
        formset=RequiredAtLeastOneInlineFormSet,
        extra=0,
        can_delete=True,
    )
    ImageFormSet = inlineformset_factory(
        Product,
        ProductImage,
        form=ProductImageForm,
        extra=0,
        can_delete=True,
    )

    product = get_object_or_404(
        Product.objects.select_related('category', 'brand').prefetch_related('variants', 'images'),
        pk=product_id,
    )

    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        variant_formset = VariantFormSet(request.POST, instance=product, prefix='variants')
        image_formset = ImageFormSet(request.POST, request.FILES, instance=product, prefix='images')

        if form.is_valid() and variant_formset.is_valid() and image_formset.is_valid():
            product = form.save()
            variant_formset.save()
            image_formset.save()

            product.refresh_availability_from_variants(save=True)
            messages.success(request, 'Product updated successfully.')
            return redirect('admin_panel:products')
    else:
        form = ProductForm(instance=product)
        variant_formset = VariantFormSet(instance=product, prefix='variants')
        image_formset = ImageFormSet(instance=product, prefix='images')

    context = {
        'form': form,
        'variant_formset': variant_formset,
        'image_formset': image_formset,
        'mode': 'edit',
        'product': product,
    }
    return render(request, 'admin/product_form.html', context)


@login_required
@user_passes_test(is_staff_user, login_url='accounts:login')
def admin_product_toggle_status(request, product_id: int):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'detail': 'Method not allowed.'}, status=405)

    product = get_object_or_404(Product, pk=product_id)
    product.is_available = not bool(product.is_available)
    product.save()

    return JsonResponse({'success': True, 'is_available': product.is_available}, status=200)


@login_required
@user_passes_test(is_staff_user, login_url='accounts:login')
def admin_product_delete(request, product_id: int):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'detail': 'Method not allowed.'}, status=405)

    product = get_object_or_404(Product, pk=product_id)
    product.delete()

    return JsonResponse({'success': True}, status=200)


@login_required
@user_passes_test(is_staff_user, login_url='accounts:login')
def admin_orders(request):
    """Admin orders management page"""
    
    orders = Order.objects.all().order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    # Filter by search
    search_query = request.GET.get('search', '')
    if search_query:
        orders = orders.filter(
            Q(user__username__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(id__icontains=search_query)
        )
    
    context = {
        'orders': orders,
        'status_filter': status_filter,
        'search_query': search_query,
    }
    
    return render(request, 'admin/orders.html', context)


@login_required
@user_passes_test(is_staff_user, login_url='accounts:login')
def admin_order_detail(request, order_id: int):
    """Admin order detail view page"""
    order = get_object_or_404(
        Order.objects.select_related('user').prefetch_related('items__product', 'items__variant'),
        pk=order_id
    )
    context = {
        'order': order,
    }
    return render(request, 'admin/order_detail.html', context)


@login_required
@user_passes_test(is_staff_user, login_url='accounts:login')
def admin_order_update_status(request, order_id: int):
    """Admin AJAX endpoint to update order status"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'detail': 'Method not allowed.'}, status=405)

    order = get_object_or_404(Order, pk=order_id)
    new_status = request.POST.get('status')

    valid_statuses = [s[0] for s in Order.STATUS_CHOICES]
    if new_status not in valid_statuses:
        return JsonResponse({'success': False, 'detail': 'Invalid status.'}, status=400)

    order.status = new_status
    order.save()

    return JsonResponse({
        'success': True,
        'status': order.status,
        'status_display': order.get_status_display()
    }, status=200)


@login_required
@user_passes_test(is_staff_user, login_url='accounts:login')
def admin_blog(request):
    """Admin blog management page"""
    
    posts = Post.objects.all().order_by('-created_at')
    
    # Filter by search
    search_query = request.GET.get('search', '')
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(author__username__icontains=search_query)
        )
    
    context = {
        'posts': posts,
        'search_query': search_query,
    }
    
    return render(request, 'admin/blog.html', context)


@login_required
@user_passes_test(is_staff_user, login_url='accounts:login')
def admin_blog_edit(request, post_id: int):
    """Admin edit blog post"""
    post = get_object_or_404(Post, pk=post_id)
    
    if request.method == 'POST':
        form = PostCreateForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Post updated successfully!')
            return redirect('admin_panel:blog')
    else:
        form = PostCreateForm(instance=post)
    
    context = {
        'form': form,
        'post': post,
        'mode': 'edit'
    }
    return render(request, 'admin/blog_form.html', context)


@login_required
@user_passes_test(is_staff_user, login_url='accounts:login')
def admin_blog_toggle_status(request, post_id: int):
    """Admin toggle blog post publish status"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'detail': 'Method not allowed.'}, status=405)
    
    post = get_object_or_404(Post, pk=post_id)
    
    # Toggle status
    if post.status == 'published':
        post.status = 'draft'
    else:
        post.status = 'published'
    
    post.save()
    
    return JsonResponse({
        'success': True,
        'status': post.status,
        'status_display': post.get_status_display()
    }, status=200)


@login_required
@user_passes_test(is_staff_user, login_url='accounts:login')
def admin_blog_delete(request, post_id: int):
    """Admin delete blog post"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'detail': 'Method not allowed.'}, status=405)
    
    post = get_object_or_404(Post, pk=post_id)
    post.delete()
    
    return JsonResponse({
        'success': True,
        'message': 'Post deleted successfully!'
    }, status=200)


@login_required
@user_passes_test(is_staff_user, login_url='accounts:login')
def notification_api(request):
    """API endpoint for notifications"""
    if request.method == 'GET':
        # Get recent notifications from database
        notifications = Notification.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=7)
        ).order_by('-created_at')[:10]
        
        notification_data = []
        for notification in notifications:
            notification_data.append({
                'id': notification.id,
                'title': notification.title,
                'message': notification.message,
                'time_ago': notification.time_ago,
                'is_read': notification.is_read,
                'notification_type': notification.notification_type,
                'order_id': notification.order_id,
                'product_id': notification.product_id
            })
        
        unread_count = Notification.objects.filter(is_read=False).count()
        
        return JsonResponse({
            'success': True,
            'notifications': notification_data,
            'unread_count': unread_count
        })


@login_required
@user_passes_test(is_staff_user, login_url='accounts:login')
def mark_notification_read(request, notification_id):
    """Mark a specific notification as read"""
    if request.method == 'POST':
        try:
            notification = Notification.objects.get(id=notification_id)
            notification.is_read = True
            notification.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Notification marked as read'
            })
        except Notification.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Notification not found'
            }, status=404)


@login_required
@user_passes_test(is_staff_user, login_url='accounts:login')
def mark_all_notifications_read(request):
    """Mark all notifications as read"""
    if request.method == 'POST':
        Notification.objects.filter(is_read=False).update(is_read=True)
        
        return JsonResponse({
            'success': True,
            'message': 'All notifications marked as read'
        })


@csrf_exempt
@login_required
@user_passes_test(is_staff_user, login_url='accounts:login')
def notification_stream(request):
    """Server-Sent Events for real-time notifications"""
    def event_stream():
        last_notification_id = 0
        
        while True:
            # Get new notifications
            new_notifications = Notification.objects.filter(
                id__gt=last_notification_id
            ).order_by('-created_at')
            
            for notification in new_notifications:
                # Send notification to client
                data = {
                    'id': notification.id,
                    'title': notification.title,
                    'message': notification.message,
                    'time_ago': notification.time_ago,
                    'is_read': notification.is_read,
                    'notification_type': notification.notification_type,
                    'order_id': notification.order_id,
                    'product_id': notification.product_id
                }
                
                yield f"data: {json.dumps(data)}\n\n"
                last_notification_id = notification.id
            
            # Check for new notifications every 5 seconds
            time.sleep(5)
    
    response = HttpResponse(event_stream(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    response['Connection'] = 'keep-alive'
    return response
