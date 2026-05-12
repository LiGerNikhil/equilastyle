from django import forms
from .models import Order


class OrderCreateForm(forms.ModelForm):
    payment_method = forms.ChoiceField(
        choices=[('cod', 'Cash on Delivery'), ('online', 'Online Payment (Razorpay)')],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='cod'
    )

    class Meta:
        model = Order
        fields = ['shipping_address', 'billing_address', 'phone_number', 'email', 'notes', 'payment_method']
        widgets = {
            'shipping_address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'billing_address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Any special instructions...'}),
        }
