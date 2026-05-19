from django import forms

from products.models import Product


class MerchantProductForm(forms.ModelForm):
    """Merchant-facing product form (no direct publish — admin approves)."""

    class Meta:
        model = Product
        fields = [
            'name',
            'description',
            'price',
            'original_price',
            'category',
            'target_group',
            'gender',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 6}),
            'original_price': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'price': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')
