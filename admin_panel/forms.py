from django import forms
from django.forms import BaseInlineFormSet

from products.models import Product, ProductImage, ProductVariant


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name',
            'description',
            'price',
            'category',
            'target_group',
            'gender',
            'is_available',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 6}),
        }


class ProductVariantForm(forms.ModelForm):
    class Meta:
        model = ProductVariant
        fields = ['size', 'stock', 'is_available']


class RequiredAtLeastOneInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return

        has_any = False
        for form in self.forms:
            if getattr(form, 'cleaned_data', None) and not form.cleaned_data.get('DELETE', False):
                if form.cleaned_data.get('size'):
                    has_any = True
                    break

        if not has_any:
            raise forms.ValidationError('Add at least one size/stock variant.')


class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image', 'alt_text', 'is_featured']
