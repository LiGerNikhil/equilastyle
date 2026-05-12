import os
import django
import requests
from django.core.files.base import ContentFile
from decimal import Decimal

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'equila_fashion.settings')
django.setup()

from products.models import Product, Category, Brand, ProductVariant, ProductImage

# Final batch of products to reach 100+
final_products = [
    # More Men's Products
    {
        'name': 'Classic Leather Belt',
        'description': 'Genuine leather belt with classic buckle.',
        'price': Decimal('39.99'),
        'original_price': Decimal('59.99'),
        'category': 'accessories',
        'gender': 'MALE',
        'target_group': 'MEN',
        'brand': 'Coach',
        'image_url': 'https://images.unsplash.com/photo-1590736928618-3b7c55b4821b?w=800&h=600&fit=crop',
        'variants': [
            {'size': 'One Size', 'stock': 25},
        ]
    },
    {
        'name': 'Sports Watch',
        'description': 'Digital sports watch with heart rate monitor.',
        'price': Decimal('129.99'),
        'original_price': Decimal('199.99'),
        'category': 'accessories',
        'gender': 'MALE',
        'target_group': 'MEN',
        'brand': 'Fitbit',
        'image_url': 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800&h=600&fit=crop',
        'variants': [
            {'size': 'One Size', 'stock': 15},
        ]
    },
    
    # More Women's Products
    {
        'name': 'Designer Handbag',
        'description': 'Elegant leather handbag for any occasion.',
        'price': Decimal('149.99'),
        'original_price': Decimal('229.99'),
        'category': 'accessories',
        'gender': 'FEMALE',
        'target_group': 'WOMEN',
        'brand': 'Michael Kors',
        'image_url': 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=800&h=600&fit=crop',
        'variants': [
            {'size': 'One Size', 'stock': 12},
        ]
    },
    {
        'name': 'Fashion Sunglasses',
        'description': 'Trendy sunglasses with UV protection.',
        'price': Decimal('79.99'),
        'original_price': Decimal('119.99'),
        'category': 'accessories',
        'gender': 'FEMALE',
        'target_group': 'WOMEN',
        'brand': 'Ray-Ban',
        'image_url': 'https://images.unsplash.com/photo-1473496169904-658ba7c44d8f?w=800&h=600&fit=crop',
        'variants': [
            {'size': 'One Size', 'stock': 20},
        ]
    },
    
    # More Kids' Products
    {
        'name': 'Kids Backpack',
        'description': 'Colorful backpack perfect for school.',
        'price': Decimal('34.99'),
        'original_price': Decimal('49.99'),
        'category': 'accessories',
        'gender': 'KIDS_BOY',
        'target_group': 'KIDS',
        'brand': 'Disney',
        'image_url': 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=800&h=600&fit=crop',
        'variants': [
            {'size': 'One Size', 'stock': 18},
        ]
    },
    {
        'name': 'Kids Water Bottle',
        'description': 'BPA-free water bottle with fun designs.',
        'price': Decimal('14.99'),
        'original_price': Decimal('24.99'),
        'category': 'accessories',
        'gender': 'KIDS_GIRL',
        'target_group': 'KIDS',
        'brand': 'Contigo',
        'image_url': 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800&h=600&fit=crop',
        'variants': [
            {'size': 'One Size', 'stock': 25},
        ]
    },
    
    # Additional Men's Shoes
    {
        'name': 'Dress Shoes',
        'description': 'Classic leather dress shoes for formal events.',
        'price': Decimal('119.99'),
        'original_price': Decimal('179.99'),
        'category': 'shoes',
        'gender': 'MALE',
        'target_group': 'MEN',
        'brand': 'Allen Edmonds',
        'image_url': 'https://images.unsplash.com/photo-1549298916-b41d501d3772?w=800&h=600&fit=crop',
        'variants': [
            {'size': 'US 8', 'stock': 10},
            {'size': 'US 9', 'stock': 12},
            {'size': 'US 10', 'stock': 15},
            {'size': 'US 11', 'stock': 8},
        ]
    },
    {
        'name': 'Basketball Shoes',
        'description': 'High-performance basketball shoes.',
        'price': Decimal('139.99'),
        'original_price': Decimal('199.99'),
        'category': 'shoes',
        'gender': 'MALE',
        'target_group': 'MEN',
        'brand': 'Under Armour',
        'image_url': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800&h=600&fit=crop',
        'variants': [
            {'size': 'US 8', 'stock': 12},
            {'size': 'US 9', 'stock': 14},
            {'size': 'US 10', 'stock': 16},
            {'size': 'US 11', 'stock': 10},
        ]
    },
    
    # Additional Women's Shoes
    {
        'name': 'Wedges',
        'description': 'Comfortable wedges for summer fashion.',
        'price': Decimal('69.99'),
        'original_price': Decimal('99.99'),
        'category': 'shoes',
        'gender': 'FEMALE',
        'target_group': 'WOMEN',
        'brand': 'Nine West',
        'image_url': 'https://images.unsplash.com/photo-1543163521-1bf539c559eb?w=800&h=600&fit=crop',
        'variants': [
            {'size': 'US 6', 'stock': 15},
            {'size': 'US 7', 'stock': 18},
            {'size': 'US 8', 'stock': 20},
            {'size': 'US 9', 'stock': 12},
        ]
    },
    {
        'name': 'Platform Sneakers',
        'description': 'Trendy platform sneakers with extra height.',
        'price': Decimal('89.99'),
        'original_price': Decimal('129.99'),
        'category': 'shoes',
        'gender': 'FEMALE',
        'target_group': 'WOMEN',
        'brand': 'Puma',
        'image_url': 'https://images.unsplash.com/photo-1594634312681-4a300995a5e2?w=800&h=600&fit=crop',
        'variants': [
            {'size': 'US 6', 'stock': 10},
            {'size': 'US 7', 'stock': 15},
            {'size': 'US 8', 'stock': 18},
            {'size': 'US 9', 'stock': 12},
        ]
    },
    
    # Additional Clothing
    {
        'name': 'Men\'s Cargo Pants',
        'description': 'Utility cargo pants with multiple pockets.',
        'price': Decimal('59.99'),
        'original_price': Decimal('89.99'),
        'category': 'clothing',
        'gender': 'MALE',
        'target_group': 'MEN',
        'brand': 'Carhartt',
        'image_url': 'https://images.unsplash.com/photo-1594634312681-4a300995a5e2?w=800&h=600&fit=crop',
        'variants': [
            {'size': 'S', 'stock': 15},
            {'size': 'M', 'stock': 20},
            {'size': 'L', 'stock': 18},
            {'size': 'XL', 'stock': 12},
        ]
    },
    {
        'name': 'Women\'s Leggings',
        'description': 'High-waisted leggings for workout and casual wear.',
        'price': Decimal('44.99'),
        'original_price': Decimal('64.99'),
        'category': 'clothing',
        'gender': 'FEMALE',
        'target_group': 'WIDS',
        'brand': 'Nike',
        'image_url': 'https://images.unsplash.com/photo-1571902943202-507ec2618e8f?w=800&h=600&fit=crop',
        'variants': [
            {'size': 'XS', 'stock': 20},
            {'size': 'S', 'stock': 25},
            {'size': 'M', 'stock': 22},
            {'size': 'L', 'stock': 18},
        ]
    },
]

def create_products():
    print('Creating final batch of products...')
    
    # Get categories and brands
    categories = Category.objects.all()
    brands = {brand.name: brand for brand in Brand.objects.all()}
    
    # Create accessories category if it doesn't exist
    accessories_category, created = Category.objects.get_or_create(
        name='accessories',
        defaults={'slug': 'accessories', 'description': 'Fashion accessories and gadgets'}
    )
    
    created_count = 0
    for product_data in final_products:
        try:
            # Find category
            category_name = product_data['category']
            if category_name == 'accessories':
                category = accessories_category
            else:
                category = categories.get(name__iexact=category_name)
            
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
    
    print(f'Successfully created {created_count} final products!')

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
