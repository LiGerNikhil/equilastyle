from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.text import slugify

User = get_user_model()


class Category(models.Model):
    GENDER_CHOICES = [
        ('M', 'Men'),
        ('W', 'Women'),
        ('K', 'Kids'),
        ('U', 'Unisex'),
    ]
    
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    logo = models.ImageField(upload_to='brands/', blank=True)
    description = models.TextField(blank=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Product(models.Model):
    TARGET_GROUP_CHOICES = [
        ('MEN', 'Men'),
        ('WOMEN', 'Women'),
        ('KIDS', 'Kids'),
        ('UNISEX', 'Unisex'),
    ]

    GENDER_CHOICES = [
        ('MALE', 'Male'),
        ('FEMALE', 'Female'),
        ('KIDS_BOY', 'Kids Boy'),
        ('KIDS_GIRL', 'Kids Girl'),
        ('UNISEX', 'Unisex'),
    ]
    
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    target_group = models.CharField(max_length=10, choices=TARGET_GROUP_CHOICES, default='MEN')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='MALE')
    is_available = models.BooleanField(default=True)
    is_premium = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def get_discount_percentage(self):
        if self.original_price and self.original_price > self.price:
            return int((self.original_price - self.price) / self.original_price * 100)
        return 0

    def clean(self):
        super().clean()
        if self.target_group == 'KIDS' and self.gender not in {'KIDS_BOY', 'KIDS_GIRL'}:
            raise ValidationError({'gender': 'Kids target group must use Kids Boy or Kids Girl.'})
        if self.target_group in {'MEN', 'WOMEN'} and self.gender in {'KIDS_BOY', 'KIDS_GIRL'}:
            raise ValidationError({'gender': 'Kids gender options are only valid for Kids target group.'})
        if self.target_group == 'MEN' and self.gender != 'MALE':
            raise ValidationError({'gender': 'Men target group must use Male gender.'})
        if self.target_group == 'WOMEN' and self.gender != 'FEMALE':
            raise ValidationError({'gender': 'Women target group must use Female gender.'})

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)[:50] or 'product'
            slug = base
            i = 2
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{i}"[:60]
                i += 1
            self.slug = slug

        # Keep legacy field aligned for existing templates/views.
        self.is_active = bool(self.is_available)
        super().save(*args, **kwargs)

    def refresh_availability_from_variants(self, *, save=True):
        has_stock = self.variants.filter(is_available=True, stock__gt=0).exists()
        self.is_available = has_stock
        self.is_active = bool(self.is_available)
        if save:
            Product.objects.filter(pk=self.pk).update(is_available=self.is_available, is_active=self.is_active)


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=200, blank=True)
    is_featured = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.product.name} - Image"


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    size = models.CharField(max_length=10)
    color = models.CharField(max_length=50, blank=True, default='')
    stock = models.PositiveIntegerField(default=0)
    sku = models.CharField(max_length=50, unique=True, blank=True, null=True)
    is_available = models.BooleanField(default=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['product', 'size'], name='uniq_variant_product_size'),
        ]
    
    def __str__(self):
        return f"{self.product.name} - {self.size} - {self.color}"

    @staticmethod
    def allowed_sizes_for_category(category_name: str):
        name = (category_name or '').strip().lower()

        clothing = {'t-shirt', 'tshirt', 'shirt'}
        pants = {'pants', 'jeans'}
        shoes = {'shoes'}

        if name in clothing:
            return ['S', 'M', 'L', 'XL', 'XXL']
        if name in pants:
            return ['28', '30', '32', '34', '36']
        if name in shoes:
            return None
        return None

    def clean(self):
        super().clean()
        if not self.product_id:
            return

        allowed = self.allowed_sizes_for_category(getattr(self.product.category, 'name', ''))
        if allowed is not None and self.size not in allowed:
            raise ValidationError({'size': f"Invalid size for category '{self.product.category}'. Allowed: {', '.join(allowed)}."})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        self.product.refresh_availability_from_variants(save=True)


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified_purchase = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['product', 'user']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.product.name} - {self.user.email} - {self.rating} stars"


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlist_items')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'product']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.product.name}"
