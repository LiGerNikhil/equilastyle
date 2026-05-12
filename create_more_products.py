import os
import django
import requests
from django.core.files.base import ContentFile
from decimal import Decimal

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'equila_fashion.settings')
django.setup()

from products.models import Product, Category, Brand, ProductVariant, ProductImage

# Additional products to reach 100+
more_products = [
    # More Men's Shoes
    {
        'name': 'Canvas Casual Sneakers',
        'description': 'Comfortable canvas sneakers for everyday wear.',
        'price': Decimal('69.99'),
        'original_price': Decimal('99.99'),
        'category': 'shoes',
        'gender': 'MALE',
        'target_group': 'MEN',
        'brand': 'Converse',
        'image_url': 'https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?w=800&h=600&fit=crop',
        'variants': [
            {'size': 'US 8', 'stock': 15},
            {'size': 'US 9', 'stock': 20},
            {'size': 'US 10', 'stock': 18},
            {'size': 'US 11', 'stock': 12},
        ]
    },
    {
        'name': 'Trail Running Shoes',
        'description': 'Durable trail shoes for outdoor adventures.',
        'price': Decimal('129.99'),
        'original_price': Decimal('179.99'),
        'category': 'shoes',
        'gender': 'MALE',
        'target_group': 'MEN',
        'brand': 'Salomon',
        'image_url': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800&h=600&fit=crop',
        'variants': [
            {'size': 'US 8', 'stock': 10},
            {'size': 'US 9', 'stock': 12},
            {'size': 'US 10', 'stock': 15},
            {'size': 'US 11', 'stock': 8},
        ]
    },
    
    # More Women's Shoes
    {
        'name': 'Ankle Boots',
        'description': 'Stylish ankle boots for fall and winter.',
        'price': Decimal('99.99'),
        'original_price': Decimal('149.99'),
        'category': 'shoes',
        'gender': 'FEMALE',
        'target_group': 'WOMEN',
        'brand': 'Timberland',
        'image_url': 'https://images.unsplash.com/photo-1543163521-1bf539c559eb?w=800&h=600&fit=crop',
        'variants': [
            {'size': 'US 6', 'stock': 12},
            {'size': 'US 7', 'stock': 15},
            {'size': 'US 8', 'stock': 18},
            {'size': 'US 9', 'stock': 10},
        ]
    },
    {
        'name': 'Sport Sandals',
        'description': 'Comfortable sandals for beach and casual wear.',
        'price': Decimal('49.99'),
        'original_price': Decimal('79.99'),
        'category': 'shoes',
        'gender': 'FEMALE',
        'target_group': 'WOMEN',
        'brand': 'Crocs',
        'image_url': 'https://images.unsplash.com/photo-1594634312681-4a300995a5e2?w=800&h=600&fit=crop',
        'variants': [
            {'size': 'US 6', 'stock': 20},
            {'size': 'US 7', 'stock': 25},
            {'size': 'US 8', 'stock': 22},
            {'size': 'US 9', 'stock': 15},
        ]
    },
    
    # More Kids' Products
    {
        'name': 'Kids Athletic Shoes',
        'description': 'Lightweight athletic shoes for active kids.',
        'price': Decimal('44.99'),
        'original_price': Decimal('64.99'),
        'category': 'shoes',
        'gender': 'KIDS_BOY',
        'target_group': 'KIDS',
        'brand': 'New Balance',
        'image_url': 'https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?w=800&h=600&fit=crop',
        'variants': [
            {'size': 'US 1', 'stock': 18},
            {'size': 'US 2', 'stock': 22},
            {'size': 'US 3', 'stock': 20},
            {'size': 'US 4', 'stock': 16},
        ]
    },
    {
        'name': 'Kids Hoodie',
        'description': 'Cozy hoodie perfect for school and play.',
        'price': Decimal('29.99'),
        'original_price': Decimal('44.99'),
        'category': 'clothing',
        'gender': 'KIDS_BOY',
        'target_group': 'KIDS',
        'brand': 'Carter\'s',
        'image_url': 'https://images.unsplash.com/photo-1515372039744-b8e02a3ae446?w=800&h=600&fit=crop',
        'variants': [
            {'size': '2T', 'stock': 25},
            {'size': '3T', 'stock': 30},
            {'size': '4T', 'stock': 28},
            {'size': '5T', 'stock': 20},
        ]
    },
    
    # More Men's Clothing
    {
        'name': 'Casual Polo Shirt',
        'description': 'Classic polo shirt for smart casual look.',
        'price': Decimal('39.99'),
        'original_price': Decimal('59.99'),
        'category': 'clothing',
        'gender': 'MALE',
        'target_group': 'MEN',
        'brand': 'Tommy Hilfiger',
        'image_url': 'https://images.unsplash.com/photo-1596755094514-f87e340cc589c?w=800&h=600&fit=crop',
        'variants': [
            {'size': 'S', 'stock': 18},
            {'size': 'M', 'stock': 25},
            {'size': 'L', 'stock': 22},
            {'size': 'XL', 'stock': 15},
        ]
    },
    {
        'name': 'Winter Jacket',
        'description': 'Warm winter jacket with modern style.',
        'price': Decimal('149.99'),
        'original_price': Decimal('229.99'),
        'category': 'clothing',
        'gender': 'MALE',
        'target_group': 'MEN',
        'brand': 'North Face',
        'image_url': 'https://images.unsplash.com/photo-1546868871-7041f2a55e12?w=800&h=600&fit=crop',
        'variants': [
            {'size': 'S', 'stock': 12},
            {'size': 'M', 'stock': 16},
            {'size': 'L', 'stock': 14},
            {'size': 'XL', 'stock': 10},
        ]
    },
    
    # More Women's Clothing
    {
        'name': 'Casual Blazer',
        'description': 'Professional blazer for work and formal events.',
        'price': Decimal('89.99'),
        'original_price': Decimal('129.99'),
        'category': 'clothing',
        'gender': 'FEMALE',
        'target_group': 'WOMEN',
        'brand': 'Banana Republic',
        'image_url': 'https://images.unsplash.com/photo-1434389677669-e08b4cac3105?w=800&h=600&fit=crop',
        'variants': [
            {'size': 'XS', 'stock': 10},
            {'size': 'S', 'stock': 15},
            {'size': 'M', 'stock': 18},
            {'size': 'L', 'stock': 12},
        ]
    },
    {
        'name': 'Summer Shorts',
        'description': 'Comfortable shorts perfect for summer days.',
        'price': Decimal('34.99'),
        'original_price': Decimal('54.99'),
        'category': 'clothing',
        'gender': 'FEMALE',
        'target_group': 'WOMEN',
        'brand': 'Forever 21',
        'image_url': 'https://images.unsplash.com/photo-1490481652071-3d5dccb40c20?w=800&h=600&fit=crop',
        'variants': [
            {'size': 'XS', 'stock': 20},
            {'size': 'S', 'stock': 25},
            {'size': 'M', 'stock': 22},
            {'size': 'L', 'stock': 18},
        ]
    },
]

def create_products():
    print('Creating additional products...')
    
    # Get categories and brands
    categories = Category.objects.all()
    brands = {brand.name: brand for brand in Brand.objects.all()}
    
    created_count = 0
    for product_data in more_products:
        try:
            # Find category
            category = categories.get(name__iexact=product_data['category'])
            
            # Get or create brand
            brand_name = product_data['brand']
            brand, created = Brand.objects.get_or_create(
                name=brand_name,
                defaults={'slug': brand_name.lower().replace(' ', '-').replace('\'', '')}
            )
            
            # Create product
            product = Product.objects.create(
                name=product_data['name'],
                description=product_data['description'],
                price=product_data['price'],
                original_price=product_data['original_price'],
                category=category,
                gender=product_data['gender'],
                target_group=product_data['target_group'],
                brand=brand,
                is_active=True,
                is_available=True,
                is_premium=False
            )
            
            # Download and save image
            download_and_save_image(product, product_data['image_url'])
            
            # Create variants
            for variant_data in product_data['variants']:
                ProductVariant.objects.create(
                    product=product,
                    size=variant_data['size'],
                    stock=variant_data['stock']
                )
            
            created_count += 1
            print(f'Created product: {product.name}')
            
        except Exception as e:
            print(f'Error creating product {product_data.get("name", "Unknown")}: {str(e)}')
    
    print(f'Successfully created {created_count} additional products!')

def download_and_save_image(product, image_url):
    """Download image from URL and save to product"""
    try:
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            # Get filename from URL or create one
            filename = f"{product.slug}.jpg"
            
            # Save image
            product_image = ProductImage(
                product=product,
                alt_text=product.name
            )
            product_image.image.save(filename, ContentFile(response.content), save=True)
            print(f'  - Saved image for {product.name}')
        else:
            print(f'  - Failed to download image for {product.name}')
    except Exception as e:
        print(f'  - Error downloading image for {product.name}: {str(e)}')

if __name__ == '__main__':
    create_products()
