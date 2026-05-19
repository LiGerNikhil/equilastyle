from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from accounts.models import User
from merchants.models import Merchant, Territory
from merchants.user_account import provision_merchant_owner


class MerchantForm(forms.ModelForm):
    """Admin form: creates merchant record + owner login (email + password)."""

    login_email = forms.EmailField(
        label='Login email',
        help_text='Merchant signs in with this email and the password below.',
    )
    login_password = forms.CharField(
        label='Login password',
        widget=forms.PasswordInput(render_value=True),
        required=False,
        help_text='Required when creating a merchant. Leave blank on edit to keep the current password.',
    )
    login_password_confirm = forms.CharField(
        label='Confirm password',
        widget=forms.PasswordInput(render_value=True),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name in ('login_password', 'login_password_confirm'):
                field.widget.attrs.setdefault('class', 'form-control')
                field.widget.attrs.setdefault('autocomplete', 'new-password')
            elif not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault('class', 'form-control')

        # Remove manual owner_user picker — provisioned automatically
        if 'owner_user' in self.fields:
            del self.fields['owner_user']

        if self.instance and self.instance.pk:
            if self.instance.owner_user_id:
                self.fields['login_email'].initial = self.instance.owner_user.email
            else:
                self.fields['login_email'].initial = self.instance.email
            self.fields['login_password'].required = False
        else:
            self.fields['login_password'].required = True

    class Meta:
        model = Merchant
        fields = [
            'business_name',
            'owner_name',
            'email',
            'phone',
            'gst_number',
            'franchise_type',
            'commission_rate',
            'territory',
            'address',
            'city',
            'state',
            'country',
            'pincode',
            'logo',
            'banner',
            'store_policy',
            'about_text',
            'status',
            'verification_status',
            'regional_manager',
        ]
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'store_policy': forms.Textarea(attrs={'rows': 4}),
            'about_text': forms.Textarea(attrs={'rows': 4}),
            'commission_rate': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'max': '100'}),
        }

    def clean_login_email(self):
        email = self.cleaned_data['login_email'].strip().lower()
        qs = User.objects.filter(email__iexact=email)
        if self.instance and self.instance.pk and self.instance.owner_user_id:
            qs = qs.exclude(pk=self.instance.owner_user_id)
        if qs.exists():
            raise ValidationError('This email is already used by another account.')
        return email

    def clean(self):
        cleaned = super().clean()
        password = cleaned.get('login_password') or ''
        confirm = cleaned.get('login_password_confirm') or ''
        is_create = not (self.instance and self.instance.pk)

        if is_create and not password:
            self.add_error('login_password', 'Password is required when creating a merchant account.')

        if password or confirm:
            if password != confirm:
                self.add_error('login_password_confirm', 'Passwords do not match.')
            if password:
                validate_password(password)

        return cleaned

    def save(self, commit=True):
        merchant = super().save(commit=commit)
        if not commit:
            return merchant

        login_email = self.cleaned_data['login_email']
        password = self.cleaned_data.get('login_password') or None
        provision_merchant_owner(
            merchant=merchant,
            login_email=login_email,
            password=password,
            update_password=bool(password),
        )
        return merchant


class TerritoryForm(forms.ModelForm):
    class Meta:
        model = Territory
        fields = ['name', 'description', 'merchant_limit', 'is_exclusive', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
