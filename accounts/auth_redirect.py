"""Post-login redirect based on user role."""
from django.shortcuts import redirect

from accounts.models import User


def redirect_after_login(user):
    from merchants.permissions import get_merchant_for_user, is_super_admin

    if is_super_admin(user) or user.is_staff:
        return redirect('admin_panel:dashboard')

    if user.role in (User.Role.MERCHANT, User.Role.MERCHANT_STAFF):
        if get_merchant_for_user(user):
            return redirect('merchants:dashboard')

    return redirect('products:home')
