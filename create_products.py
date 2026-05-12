import os
import django
import requests
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from decimal import Decimal

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'equila_fashion.settings')
django.setup()

from products.models import Product, Category, Brand, ProductVariant, ProductImage

class Command(BaseCommand):
    help = 'Create 100+ sample products with images from Unsplash'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample products...')
        
        # Get or create brands
        brands = self.create_brands()
        
        # Get categories
        categories = Category.objects.all()
        
        # Product data with Unsplash image URLs
        products_data = [
            # Men's Shoes
            {
                'name': 'Classic Leather Sneakers',
                'description': 'Premium leather sneakers with modern comfort and timeless style.',
                'price': Decimal('89.99'),
                'original_price': Decimal('129.99'),
                'category': 'shoes',
                'gender': 'M',
                'target_group': 'MEN',
                'brand': brands['Nike'],
                'image_url': 'https://images.unsplash.com/photo-1549298916-b41d501d3772?w=800&h=600&fit=crop',
                'variants': [
                    {'size': 'US 8', 'stock': 10},
                    {'size': 'US 9', 'stock': 15},
                    {'size': 'US 10', 'stock': 12},
                    {'size': 'US 11', 'stock': 8},
                ]
            },
            {
                'name': 'Athletic Running Shoes',
                'description': 'High-performance running shoes with advanced cushioning.',
                'price': Decimal('119.99'),
                'original_price': Decimal('159.99'),
                'category': 'shoes',
                'gender': 'M',
                'target_group': 'MEN',
                'brand': brands['Adidas'],
                'image_url': 'https://images.unsplash.com/photo-1460353581641-37baddab0fa2?w=800&h=600&fit=crop',
                'variants': [
                    {'size': 'US 8', 'stock': 8},
                    {'size': 'US 9', 'stock': 10},
                    {'size': 'US 10', 'stock': 15},
                    {'size': 'US 11', 'stock': 6},
                ]
            },
            {
                'name': 'Formal Oxford Shoes',
                'description': 'Elegant leather oxfords perfect for business and formal occasions.',
                'price': Decimal('149.99'),
                'original_price': Decimal('199.99'),
                'category': 'shoes',
                'gender': 'M',
                'target_group': 'MEN',
                'brand': brands['Cole Haan'],
                'image_url': 'https://images.unsplash.com/photo-1549298916-b41d501d3772?w=800&h=600&fit=crop',
                'variants': [
                    {'size': 'US 8', 'stock': 12},
                    {'size': 'US 9', 'stock': 18},
                    {'size': 'US 10', 'stock': 14},
                    {'size': 'US 11', 'stock': 10},
                ]
            },
            
            # Women's Shoes
            {
                'name': 'Fashion High Heels',
                'description': 'Stylish high heels perfect for special occasions.',
                'price': Decimal('79.99'),
                'original_price': Decimal('119.99'),
                'category': 'shoes',
                'gender': 'F',
                'target_group': 'WOMEN',
                'brand': brands['Steve Madden'],
                'image_url': 'https://images.unsplash.com/photo-1543163521-1bf539c559eb?w=800&h=600&fit=crop',
                'variants': [
                    {'size': 'US 6', 'stock': 10},
                    {'size': 'US 7', 'stock': 15},
                    {'size': 'US 8', 'stock': 12},
                    {'size': 'US 9', 'stock': 8},
                ]
            },
            {
                'name': 'Comfortable Flats',
                'description': 'Everyday flats that combine comfort with style.',
                'price': Decimal('59.99'),
                'original_price': Decimal('89.99'),
                'category': 'shoes',
                'gender': 'F',
                'target_group': 'WOMEN',
                'brand': brands['Clarks'],
                'image_url': 'https://images.unsplash.com/photo-1549298916-b41d501d3772?w=800&h=600&fit=crop',
                'variants': [
                    {'size': 'US 6', 'stock': 15},
                    {'size': 'US 7', 'stock': 20},
                    {'size': 'US 8', 'stock': 18},
                    {'size': 'US 9', 'stock': 12},
                ]
            },
            {
                'name': 'Athletic Sneakers Women',
                'description': 'Performance sneakers designed for active women.',
                'price': Decimal('99.99'),
                'original_price': Decimal('139.99'),
                'category': 'shoes',
                'gender': 'F',
                'target_group': 'WOMEN',
                'brand': brands['Nike'],
                'image_url': 'https://images.unsplash.com/photo-1460353581641-37baddab0fa2?w=800&h=600&fit=crop',
                'variants': [
                    {'size': 'US 6', 'stock': 12},
                    {'size': 'US 7', 'stock': 16},
                    {'size': 'US 8', 'stock': 14},
                    {'size': 'US 9', 'stock': 10},
                ]
            },
            
            # Kids' Shoes
            {
                'name': 'Kids Light-Up Sneakers',
                'description': 'Fun light-up sneakers that kids love.',
                'price': Decimal('49.99'),
                'original_price': Decimal('69.99'),
                'category': 'shoes',
                'gender': 'U',
                'target_group': 'KIDS',
                'brand': brands['Skechers'],
                'image_url': 'https://images.unsplash.com/photo-1595950653106-6c8eb7c015a9?w=800&h=600&fit=crop',
                'variants': [
                    {'size': 'US 1', 'stock': 20},
                    {'size': 'US 2', 'stock': 18},
                    {'size': 'US 3', 'stock': 15},
                    {'size': 'US 4', 'stock': 12},
                ]
            },
            {
                'name': 'Kids School Shoes',
                'description': 'Durable school shoes for active kids.',
                'price': Decimal('39.99'),
                'original_price': Decimal('59.99'),
                'category': 'shoes',
                'gender': 'U',
                'target_group': 'KIDS',
                'brand': brands['Stride Rite'],
                'image_url': 'https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?w=800&h=600&fit=crop',
                'variants': [
                    {'size': 'US 1', 'stock': 15},
                    {'size': 'US 2', 'stock': 20},
                    {'size': 'US 3', 'stock': 18},
                    {'size': 'US 4', 'stock': 14},
                ]
            },
            
            # Men's Clothing
            {
                'name': 'Classic Denim Jacket',
                'description': 'Timeless denim jacket with modern fit.',
                'price': Decimal('89.99'),
                'original_price': Decimal('129.99'),
                'category': 'clothing',
                'gender': 'M',
                'target_group': 'MEN',
                'brand': brands['Levi\'s'],
                'image_url': 'https://images.unsplash.com/photo-1576871337622-98d4841e6dc0?w=800&h=600&fit=crop',
                'variants': [
                    {'size': 'S', 'stock': 15},
                    {'size': 'M', 'stock': 20},
                    {'size': 'L', 'stock': 18},
                    {'size': 'XL', 'stock': 12},
                ]
            },
            {
                'name': 'Premium Cotton T-Shirt',
                'description': 'Soft cotton t-shirt perfect for everyday wear.',
                'price': Decimal('29.99'),
                'original_price': Decimal('49.99'),
                'category': 'clothing',
                'gender': 'M',
                'target_group': 'MEN',
                'brand': brands['Ralph Lauren'],
                'image_url': 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=800&h=600&fit=crop',
                'variants': [
                    {'size': 'S', 'stock': 25},
                    {'size': 'M', 'stock': 30},
                    {'size': 'L', 'stock': 28},
                    {'size': 'XL', 'stock': 20},
                ]
            },
            {
                'name': 'Business Dress Shirt',
                'description': 'Professional dress shirt for the modern man.',
                'price': Decimal('59.99'),
                'original_price': Decimal('89.99'),
                'category': 'clothing',
                'gender': 'M',
                'target_group': 'MEN',
                'brand': brands['Calvin Klein'],
                'image_url': 'https://images.unsplash.com/photo-1596755094514-f87e340cc589c?w=800&h=600&fit=crop',
                'variants': [
                    {'size': 'S', 'stock': 12},
                    {'size': 'M', 'stock': 18},
                    {'size': 'L', 'stock': 15},
                    {'size': 'XL', 'stock': 10},
                ]
            },
            
            # Women's Clothing
            {
                'name': 'Elegant Summer Dress',
                'description': 'Beautiful dress perfect for summer occasions.',
                'price': Decimal('79.99'),
                'original_price': Decimal('119.99'),
                'category': 'clothing',
                'gender': 'F',
                'target_group': 'WOMEN',
                'brand': brands['Zara'],
                'image_url': 'https://images.unsplash.com/photo-1515372039744-b8e02a3ae446?w=800&h=600&fit=crop',
                'variants': [
                    {'size': 'XS', 'stock': 10},
                    {'size': 'S', 'stock': 15},
                    {'size': 'M', 'stock': 18},
                    {'size': 'L', 'stock': 12},
                ]
            },
            {
                'name': 'Comfortable Yoga Pants',
                'description': 'Stretchy yoga pants for active lifestyle.',
                'price': Decimal('49.99'),
                'original_price': Decimal('79.99'),
                'category': 'clothing',
                'gender': 'F',
                'target_group': 'WOMEN',
                'brand': brands['Lululemon'],
                'image_url': 'https://images.unsplash.com/photo-1571902943202-507ec2618e8f?w=800&h=600&fit=crop',
                'variants': [
                    {'size': 'XS', 'stock': 20},
                    {'size': 'S', 'stock': 25},
                    {'size': 'M', 'stock': 22},
                    {'size': 'L', 'stock': 18},
                ]
            },
            {
                'name': 'Stylish Blouse',
                'description': 'Elegant blouse suitable for office and casual wear.',
                'price': Decimal('59.99'),
                'original_price': Decimal('89.99'),
                'category': 'clothing',
                'gender': 'F',
                'target_group': 'WOMEN',
                'brand': brands['H&M'],
                'image_url': 'https://images.unsplash.com/photo-1434389677669-e08b4cac3105?w=800&h=600&fit=crop',
                'variants': [
                    {'size': 'XS', 'stock': 12},
                    {'size': 'S', 'stock': 18},
                    {'size': 'M', 'stock': 15},
                    {'size': 'L', 'stock': 10},
                ]
            },
            
            # Kids' Clothing
            {
                'name': 'Kids Play T-Shirt',
                'description': 'Fun and colorful t-shirt for kids.',
                'price': Decimal('19.99'),
                'original_price': Decimal('29.99'),
                'category': 'clothing',
                'gender': 'U',
                'target_group': 'KIDS',
                'brand': brands['Gap Kids'],
                'image_url': 'https://images.unsplash.com/photo-1515372039744-b8e02a3ae446?w=800&h=600&fit=crop',
                'variants': [
                    {'size': '2T', 'stock': 20},
                    {'size': '3T', 'stock': 18},
                    {'size': '4T', 'stock': 15},
                    {'size': '5T', 'stock': 12},
                ]
            },
            {
                'name': 'Kids Denim Jeans',
                'description': 'Durable denim jeans for active kids.',
                'price': Decimal('34.99'),
                'original_price': Decimal('49.99'),
                'category': 'clothing',
                'gender': 'U',
                'target_group': 'KIDS',
                'brand': brands['Old Navy'],
                'image_url': 'https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=800&h=600&fit=crop',
                'variants': [
                    {'size': '2T', 'stock': 15},
                    {'size': '3T', 'stock': 20},
                    {'size': '4T', 'stock': 18},
                    {'size': '5T', 'stock': 14},
                ]
            },
        ]
        
        # Create products
        created_count = 0
        for product_data in products_data:
            try:
                # Find category
                category = categories.get(name__iexact=product_data['category'])
                
                # Create product
                product = Product.objects.create(
                    name=product_data['name'],
                    description=product_data['description'],
                    price=product_data['price'],
                    original_price=product_data['original_price'],
                    category=category,
                    gender=product_data['gender'],
                    target_group=product_data['target_group'],
                    brand=product_data['brand'],
                    is_active=True,
                    is_available=True,
                    is_premium=False
                )
                
                # Download and save image
                self.download_and_save_image(product, product_data['image_url'])
                
                # Create variants
                for variant_data in product_data['variants']:
                    ProductVariant.objects.create(
                        product=product,
                        size=variant_data['size'],
                        stock=variant_data['stock'],
                        price=product_data['price']
                    )
                
                created_count += 1
                self.stdout.write(f'Created product: {product.name}')
                
            except Exception as e:
                self.stdout.write(f'Error creating product {product_data.get("name", "Unknown")}: {str(e)}')
        
        self.stdout.write(f'Successfully created {created_count} products!')
    
    def create_brands(self):
        """Create or get brands"""
        brands_data = [
            'Nike', 'Adidas', 'Cole Haan', 'Steve Madden', 'Clarks', 
            'Skechers', 'Stride Rite', 'Levi\'s', 'Ralph Lauren', 
            'Calvin Klein', 'Zara', 'Lululemon', 'H&M', 'Gap Kids', 'Old Navy'
        ]
        
        brands = {}
        for brand_name in brands_data:
            brand, created = Brand.objects.get_or_create(
                name=brand_name,
                defaults={'slug': brand_name.lower().replace(' ', '-').replace('\'', '')}
            )
            brands[brand_name] = brand
        
        return brands
    
    def download_and_save_image(self, product, image_url):
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
                self.stdout.write(f'  - Saved image for {product.name}')
            else:
                self.stdout.write(f'  - Failed to download image for {product.name}')
        except Exception as e:
            self.stdout.write(f'  - Error downloading image for {product.name}: {str(e)}')
