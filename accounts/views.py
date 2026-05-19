from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .auth_redirect import redirect_after_login
from .forms import CustomUserCreationForm, UserUpdateForm, ProfileUpdateForm, AddressForm
from .models import Profile


@csrf_protect
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect_after_login(user)
    else:
        form = CustomUserCreationForm()
    
    # Ensure session is created for CSRF token
    request.session.set_test_cookie()
    
    return render(request, 'accounts/register.html', {'form': form})


@csrf_protect
def login_view(request):
    if request.user.is_authenticated:
        return redirect_after_login(request.user)
    
    from django.contrib.auth.forms import AuthenticationForm
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect_after_login(user)
    else:
        form = AuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def profile(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user)
    
    # Get user's addresses
    addresses = request.user.addresses.all()
    
    # Handle address form
    if 'address_form' in request.POST:
        address_form = AddressForm(request.POST)
        if address_form.is_valid():
            address = address_form.save(commit=False)
            address.user = request.user
            address.save()
            return redirect('accounts:profile')
    else:
        address_form = AddressForm()
    
    # Handle profile update
    if 'user_form' in request.POST:
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('accounts:profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=profile)
    
    # Get user's cart
    from cart.models import Cart
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # Get user's wishlist items
    from products.models import Wishlist
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product', 'product__category').prefetch_related('product__images')
    
    # Get user's orders
    from orders.models import Order
    orders = Order.objects.filter(user=request.user).prefetch_related('items').order_by('-created_at')
    recent_orders = orders[:5]  # Last 5 orders
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'address_form': address_form,
        'addresses': addresses,
        'cart': cart,
        'cart_items': cart.items.all() if not created else [],
        'wishlist_items': wishlist_items,
        'orders': orders,
        'recent_orders': recent_orders,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def wishlist(request):
    # Get user's wishlist items
    from products.models import Wishlist
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product', 'product__category').prefetch_related('product__images')
    
    # Calculate wishlist total
    wishlist_total = sum(item.product.price for item in wishlist_items)
    
    context = {
        'wishlist_items': wishlist_items,
        'wishlist_total': wishlist_total,
    }
    return render(request, 'accounts/wishlist.html', context)


@login_required
@require_POST
def remove_from_wishlist(request, product_id):
    from products.models import Wishlist
    try:
        wishlist_item = Wishlist.objects.get(user=request.user, product_id=product_id)
        wishlist_item.delete()
        return JsonResponse({'success': True})
    except Wishlist.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Item not found in wishlist'})


@login_required
@require_POST
def add_all_to_cart(request):
    from products.models import Wishlist
    from cart.models import Cart, CartItem
    
    try:
        cart, created = Cart.objects.get_or_create(user=request.user)
        wishlist_items = Wishlist.objects.filter(user=request.user)
        
        items_added = 0
        for wishlist_item in wishlist_items:
            # Check if product is in stock
            if wishlist_item.product.stock > 0:
                # Check if item already exists in cart
                cart_item, created = CartItem.objects.get_or_create(
                    cart=cart,
                    product=wishlist_item.product,
                    defaults={'quantity': 1}
                )
                if not created:
                    cart_item.quantity += 1
                    cart_item.save()
                items_added += 1
        
        return JsonResponse({'success': True, 'items_added': items_added})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_POST
def clear_wishlist(request):
    from products.models import Wishlist
    try:
        Wishlist.objects.filter(user=request.user).delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
