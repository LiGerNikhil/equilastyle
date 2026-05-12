from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from products.models import Product, ProductVariant
from .models import Cart, CartItem
from .forms import CartAddProductForm


@login_required
def cart_detail(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'cart/cart_detail.html', {'cart': cart})


@login_required
def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Try form validation first
        form = CartAddProductForm(request.POST, product=product)
        
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            variant = form.cleaned_data.get('variant')
        else:
            # Fallback: parse POST data directly for AJAX requests
            try:
                quantity = int(request.POST.get('quantity', 1))
                if quantity < 1 or quantity > 99:
                    return JsonResponse({
                        'success': False,
                        'message': 'Quantity must be between 1 and 99'
                    })
            except (ValueError, TypeError):
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid quantity provided'
                })
            
            # Parse variant
            variant = None
            variant_id = request.POST.get('variant')
            if variant_id:
                try:
                    variant = product.variants.get(id=int(variant_id))
                except (ProductVariant.DoesNotExist, ValueError):
                    return JsonResponse({
                        'success': False,
                        'message': 'Invalid size/variant selected'
                    })
        
        # Add to cart
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            variant=variant,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        # Get cart items for notification
        cart_items = []
        for item in cart.items.all()[:3]:
            cart_items.append({
                'product_name': item.product.name,
                'product_image': item.product.images.first().image.url if item.product.images.first() else '/static/images/placeholder-product.jpg',
                'quantity': item.quantity,
                'price': float(item.get_total_price()),
                'variant': item.variant.size if item.variant else None
            })
        
        return JsonResponse({
            'success': True,
            'message': f'{quantity} \u00d7 {product.name} added to cart',
            'cart_count': cart.get_total_items(),
            'cart_total': float(cart.get_total_price()),
            'cart_items': cart_items,
            'added_item': {
                'product_name': product.name,
                'product_image': product.images.first().image.url if product.images.first() else '/static/images/placeholder-product.jpg',
                'quantity': quantity,
                'price': float(product.price * quantity),
                'variant': variant.size if variant else None
            }
        })
    
    # Handle non-POST requests
    return JsonResponse({
        'success': False,
        'message': 'POST method required'
    })


@login_required
def cart_remove(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    return redirect('cart:cart_detail')


@login_required
def cart_update(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            cart_item.delete()
    
    return JsonResponse({
        'success': True,
        'total_price': cart_item.cart.get_total_price(),
        'total_items': cart_item.cart.get_total_items()
    })


@login_required
def cart_clear(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        cart.items.all().delete()
        return JsonResponse({
            'success': True,
            'message': 'Cart cleared successfully'
        })
    
    return JsonResponse({
        'success': False,
        'message': 'POST method required'
    })
