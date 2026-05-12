from django import forms
from products.models import ProductVariant


class CartAddProductForm(forms.Form):
    quantity = forms.IntegerField(
        min_value=1,
        max_value=99,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    variant = forms.ModelChoiceField(
        queryset=ProductVariant.objects.none(),
        required=False,
        empty_label="Select size/color",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        product = kwargs.pop('product', None)
        super().__init__(*args, **kwargs)
        if product:
            self.fields['variant'].queryset = product.variants.all()
