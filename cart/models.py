from django.db import models
from django.contrib.auth import get_user_model
from products.models import Product, ProductVariant

User = get_user_model()


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.email}'s Cart"
    
    def get_total_price(self):
        total = sum(item.get_total_price() for item in self.items.all())
        return total
    
    def get_total_items(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['cart', 'product', 'variant']
    
    def __str__(self):
        return f"{self.product.name} - {self.quantity}"
    
    def get_price(self):
        if self.variant:
            return self.product.price
        return self.product.price
    
    def get_total_price(self):
        return self.get_price() * self.quantity
