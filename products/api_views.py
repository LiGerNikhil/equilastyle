from __future__ import annotations

import json

from django.contrib.auth.decorators import login_required, user_passes_test
from django.forms.models import model_to_dict
from django.http import HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from .models import Product, Category, Brand, ProductImage, ProductVariant


def _staff_required(user):
    return bool(user and user.is_authenticated and user.is_staff)


def _product_payload(product: Product) -> dict:
    data = model_to_dict(
        product,
        fields=[
            'id',
            'name',
            'slug',
            'description',
            'price',
            'category',
            'brand',
            'target_group',
            'gender',
            'is_available',
            'created_at',
            'updated_at',
        ],
    )

    data['category'] = product.category_id
    data['brand'] = product.brand_id

    data['variants'] = [
        {
            'id': v.id,
            'size': v.size,
            'stock': v.stock,
            'is_available': v.is_available,
        }
        for v in product.variants.all().order_by('size')
    ]

    data['images'] = [
        {
            'id': img.id,
            'image': img.image.url if img.image else None,
            'alt_text': img.alt_text,
            'is_featured': img.is_featured,
        }
        for img in product.images.all().order_by('-is_featured', 'id')
    ]

    return data


@csrf_exempt
@login_required
@user_passes_test(_staff_required)
def products_api(request: HttpRequest) -> JsonResponse:
    if request.method == 'GET':
        qs = Product.objects.select_related('category', 'brand').prefetch_related('variants', 'images').all()
        return JsonResponse({'results': [_product_payload(p) for p in qs]}, status=200)

    if request.method == 'POST':
        try:
            payload = json.loads(request.body.decode('utf-8') or '{}')
        except json.JSONDecodeError:
            return JsonResponse({'detail': 'Invalid JSON.'}, status=400)

        product = Product(
            name=payload.get('name', ''),
            description=payload.get('description', ''),
            price=payload.get('price', 0),
            category_id=payload.get('category'),
            brand_id=payload.get('brand'),
            target_group=payload.get('target_group', 'MEN'),
            gender=payload.get('gender', 'MALE'),
            is_available=bool(payload.get('is_available', True)),
        )
        product.full_clean()
        product.save()

        for v in payload.get('variants', []) or []:
            ProductVariant.objects.create(
                product=product,
                size=str(v.get('size', '')).strip(),
                stock=int(v.get('stock', 0) or 0),
                is_available=bool(v.get('is_available', True)),
            )

        # Availability may change based on variants
        product.refresh_availability_from_variants(save=True)

        return JsonResponse(_product_payload(product), status=201)

    return JsonResponse({'detail': 'Method not allowed.'}, status=405)


@csrf_exempt
@login_required
@user_passes_test(_staff_required)
def product_api(request: HttpRequest, product_id: int) -> JsonResponse:
    product = get_object_or_404(Product.objects.prefetch_related('variants', 'images'), pk=product_id)

    if request.method == 'GET':
        return JsonResponse(_product_payload(product), status=200)

    if request.method in {'PUT', 'PATCH'}:
        try:
            payload = json.loads(request.body.decode('utf-8') or '{}')
        except json.JSONDecodeError:
            return JsonResponse({'detail': 'Invalid JSON.'}, status=400)

        for field in ['name', 'description', 'price', 'target_group', 'gender', 'is_available']:
            if field in payload:
                setattr(product, field, payload[field])

        if 'category' in payload:
            product.category_id = payload['category']
        if 'brand' in payload:
            product.brand_id = payload['brand']

        product.full_clean()
        product.save()

        if 'variants' in payload:
            product.variants.all().delete()
            for v in payload.get('variants', []) or []:
                ProductVariant.objects.create(
                    product=product,
                    size=str(v.get('size', '')).strip(),
                    stock=int(v.get('stock', 0) or 0),
                    is_available=bool(v.get('is_available', True)),
                )

        product.refresh_availability_from_variants(save=True)

        return JsonResponse(_product_payload(product), status=200)

    if request.method == 'DELETE':
        product.delete()
        return JsonResponse({}, status=204)

    return JsonResponse({'detail': 'Method not allowed.'}, status=405)


def public_product_detail(request: HttpRequest, product_id: int) -> JsonResponse:
    """Public API endpoint for product details (quick view)"""
    product = get_object_or_404(
        Product.objects.filter(is_available=True)
        .select_related('category', 'brand')
        .prefetch_related('variants', 'images'), 
        pk=product_id
    )
    
    if request.method == 'GET':
        data = _product_payload(product)
        # Add additional fields for public display
        data['category_name'] = product.category.name
        data['brand_name'] = product.brand.name if product.brand else 'No Brand'
        data['get_gender_display'] = product.get_gender_display()
        data['get_target_group_display'] = product.get_target_group_display()
        
        return JsonResponse(data, status=200)
    
    return JsonResponse({'detail': 'Method not allowed.'}, status=405)
