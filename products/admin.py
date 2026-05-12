from django import forms
from django.contrib import admin

from .models import Category, Brand, Product, ProductImage, ProductVariant, Review


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'gender', 'created_at']
    list_filter = ['gender', 'created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_featured', 'created_at']
    list_filter = ['is_featured', 'created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductVariantInlineForm(forms.ModelForm):
    class Meta:
        model = ProductVariant
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        product = getattr(self.instance, 'product', None)
        if product and getattr(product, 'category', None):
            allowed = ProductVariant.allowed_sizes_for_category(getattr(product.category, 'name', ''))
            if allowed is not None:
                self.fields['size'].widget = forms.Select(choices=[(s, s) for s in allowed])


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    form = ProductVariantInlineForm


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'brand', 'price', 'target_group', 'gender', 'is_available', 'is_active']
    list_filter = ['category', 'brand', 'target_group', 'gender', 'is_available', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ProductVariantInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category', 'brand')


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'alt_text', 'is_featured']
    list_filter = ['is_featured']
    search_fields = ['product__name', 'alt_text']


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ['product', 'size', 'stock', 'is_available', 'sku']
    list_filter = ['size', 'is_available']
    search_fields = ['product__name', 'sku']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'is_verified_purchase', 'created_at']
    list_filter = ['rating', 'is_verified_purchase', 'created_at']
    search_fields = ['product__name', 'user__email', 'title']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product', 'user')
