from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Product, Wishlist


@login_required
def add_to_wishlist(request, product_id):
    """Add product to user's wishlist"""
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id, is_available=True)
        wishlist_item, created = Wishlist.objects.get_or_create(
            user=request.user,
            product=product
        )
        
        if created:
            return JsonResponse({
                'success': True,
                'message': 'Product added to wishlist',
                'action': 'added'
            })
        else:
            # Item already in wishlist, remove it
            wishlist_item.delete()
            return JsonResponse({
                'success': True,
                'message': 'Product removed from wishlist',
                'action': 'removed'
            })
    
    return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)


@login_required
def remove_from_wishlist(request, product_id):
    """Remove product from user's wishlist"""
    if request.method == 'DELETE':
        try:
            wishlist_item = Wishlist.objects.get(
                user=request.user,
                product_id=product_id
            )
            wishlist_item.delete()
            return JsonResponse({
                'success': True,
                'message': 'Product removed from wishlist'
            })
        except Wishlist.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Product not in wishlist'
            }, status=404)
    
    return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)


@login_required
def get_wishlist(request):
    """Get user's wishlist"""
    if request.method == 'GET':
        wishlist_items = Wishlist.objects.filter(
            user=request.user
        ).select_related('product', 'product__category').prefetch_related('product__images')
        
        items = []
        for item in wishlist_items:
            product = item.product
            items.append({
                'id': item.id,
                'product_id': product.id,
                'product_name': product.name,
                'product_slug': product.slug,
                'price': float(product.price),
                'image': product.images.first().image.url if product.images.first() else None,
                'category': product.category.name,
                'created_at': item.created_at.isoformat()
            })
        
        return JsonResponse({
            'success': True,
            'items': items,
            'count': len(items)
        })
    
    return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)


@login_required
def toggle_wishlist(request, product_id):
    """Toggle product in wishlist (add if not present, remove if present)"""
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id, is_available=True)
        
        try:
            wishlist_item = Wishlist.objects.get(
                user=request.user,
                product=product
            )
            # Item exists, remove it
            wishlist_item.delete()
            return JsonResponse({
                'success': True,
                'message': 'Product removed from wishlist',
                'action': 'removed',
                'in_wishlist': False
            })
        except Wishlist.DoesNotExist:
            # Item doesn't exist, add it
            Wishlist.objects.create(
                user=request.user,
                product=product
            )
            return JsonResponse({
                'success': True,
                'message': 'Product added to wishlist',
                'action': 'added',
                'in_wishlist': True
            })
    
    return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)
