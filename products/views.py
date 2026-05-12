from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Avg, Min, Max
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import Product, Category, Brand, ProductImage, ProductVariant


def home(request):
    featured_products = Product.objects.filter(is_featured=True, is_active=True)[:8]
    premium_products = Product.objects.filter(is_premium=True, is_active=True)[:8]
    categories = Category.objects.all()[:6]
    brands = Brand.objects.filter(is_featured=True)[:6]
    
    context = {
        'featured_products': featured_products,
        'premium_products': premium_products,
        'categories': categories,
        'brands': brands,
    }
    return render(request, 'products/home.html', context)


def about(request):
    context = {}
    return render(request, 'about.html', context)


def privacy(request):
    context = {}
    return render(request, 'privacy.html', context)


def terms(request):
    context = {}
    return render(request, 'terms.html', context)


def cookies(request):
    context = {}
    return render(request, 'cookies.html', context)


def shipping(request):
    context = {}
    return render(request, 'shipping.html', context)


def returns(request):
    context = {}
    return render(request, 'returns.html', context)


def size_guide(request):
    context = {}
    return render(request, 'size-guide.html', context)


def product_list(request):
    products = Product.objects.filter(is_available=True).select_related('category', 'brand').prefetch_related('images', 'variants')
    categories = Category.objects.all()
    
    # Get filter parameters
    category_slug = request.GET.get('category')
    brand_slug = request.GET.get('brand')
    search_query = request.GET.get('search')
    target_group = request.GET.get('target_group')
    gender = request.GET.get('gender')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    sort_by = request.GET.get('sort', 'newest')
    
    # Apply filters
    if category_slug and category_slug not in ['None', 'on']:
        try:
            category = get_object_or_404(Category, slug=category_slug)
            products = products.filter(category=category)
        except:
            # If category doesn't exist, return empty queryset
            products = Product.objects.none()
    
    if brand_slug:
        brand = get_object_or_404(Brand, slug=brand_slug)
        products = products.filter(brand=brand)
    
    if target_group and target_group not in ['None', 'on']:
        products = products.filter(target_group=target_group)
    
    if gender and gender not in ['None', 'on']:
        products = products.filter(gender=gender)
    
    if min_price:
        try:
            products = products.filter(price__gte=float(min_price))
        except ValueError:
            pass
    
    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except ValueError:
            pass
    
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(brand__name__icontains=search_query)
        )
    
    # Apply sorting
    if sort_by == 'price-low':
        products = products.order_by('price')
    elif sort_by == 'price-high':
        products = products.order_by('-price')
    elif sort_by == 'name':
        products = products.order_by('name')
    else:  # newest
        products = products.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(products, 6)  # 6 products per page
    page = request.GET.get('page')
    products = paginator.get_page(page)
    
    # Get price range for filters
    price_range = Product.objects.filter(is_available=True).aggregate(
        min_price=Min('price'),
        max_price=Max('price')
    )
    
    context = {
        'products': products,
        'categories': categories,
        'selected_category': category_slug,
        'selected_brand': brand_slug,
        'selected_target_group': target_group,
        'selected_gender': gender,
        'search_query': search_query,
        'min_price': min_price,
        'max_price': max_price,
        'sort_by': sort_by,
        'price_range': price_range,
    }
    return render(request, 'products/product_list.html', context)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id)[:4]
    
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'products/product_detail.html', context)


def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category, is_active=True)
    
    context = {
        'category': category,
        'products': products,
    }
    return render(request, 'products/category_products.html', context)


def brand_products(request, slug):
    brand = get_object_or_404(Brand, slug=slug)
    products = Product.objects.filter(brand=brand, is_active=True)
    
    context = {
        'brand': brand,
        'products': products,
    }
    return render(request, 'products/brand_products.html', context)


def search_products(request):
    """AJAX search for products"""
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'message': 'Invalid request'})
    
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({
            'success': False, 
            'message': 'Please enter at least 2 characters'
        })
    
    # Search products
    products = Product.objects.filter(
        is_available=True,
        is_active=True
    ).filter(
        Q(name__icontains=query) |
        Q(description__icontains=query) |
        Q(category__name__icontains=query) |
        Q(brand__name__icontains=query)
    ).select_related('category', 'brand').prefetch_related('images', 'variants')
    
    # Prepare product data for JSON response
    products_data = []
    for product in products[:20]:  # Limit to 20 results for performance
        # Get main image
        main_image = product.images.filter(is_main=True).first()
        image_url = main_image.image.url if main_image else '/static/images/placeholder-product.jpg'
        
        # Calculate discount percentage
        discount_percentage = None
        if product.original_price and product.original_price > product.price:
            discount_percentage = int(((product.original_price - product.price) / product.original_price) * 100)
        
        products_data.append({
            'id': product.id,
            'name': product.name,
            'slug': product.slug,
            'price': str(product.price),
            'original_price': str(product.original_price) if product.original_price else None,
            'discount_percentage': discount_percentage,
            'image_url': image_url,
            'category_name': product.category.name if product.category else '',
            'brand_name': product.brand.name if product.brand else '',
            'gender_display': product.get_gender_display(),
            'target_group_display': product.get_target_group_display(),
            'is_premium': product.is_premium,
            'is_featured': product.is_featured,
        })
    
    return JsonResponse({
        'success': True,
        'products': products_data,
        'total_count': len(products_data),
        'query': query
    })
