"""
Role-based access control for multi-merchant platform.

Roles:
  - super_admin: full platform access (is_staff legacy users included)
  - regional_manager: monitor merchants in assigned territories
  - merchant: own store data only
  - merchant_staff: permissions granted by merchant
  - customer: storefront only
"""
from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect

from accounts.models import User


def get_user_role(user):
    if not user.is_authenticated:
        return User.Role.CUSTOMER
    return getattr(user, 'role', User.Role.CUSTOMER)


def is_super_admin(user):
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return get_user_role(user) == User.Role.SUPER_ADMIN or (
        user.is_staff and get_user_role(user) == User.Role.CUSTOMER
    )


def is_regional_manager(user):
    return user.is_authenticated and get_user_role(user) == User.Role.REGIONAL_MANAGER


def is_merchant(user):
    return user.is_authenticated and get_user_role(user) == User.Role.MERCHANT


def is_merchant_staff(user):
    return user.is_authenticated and get_user_role(user) == User.Role.MERCHANT_STAFF


def get_merchant_for_user(user):
    """Resolve the Merchant instance the user may operate on."""
    from merchants.models import Merchant, MerchantStaff

    if not user.is_authenticated:
        return None
    # Reverse OneToOne: User.owned_merchant (no owned_merchant_id on User)
    try:
        return user.owned_merchant
    except Merchant.DoesNotExist:
        pass
    if is_merchant_staff(user):
        staff = (
            MerchantStaff.objects.filter(user=user, is_active=True)
            .select_related('merchant')
            .first()
        )
        return staff.merchant if staff else None
    return None


def user_can_access_merchant(user, merchant):
    if is_super_admin(user):
        return True
    if is_regional_manager(user):
        if merchant.regional_manager_id == user.id:
            return True
        if merchant.territory_id and user.managed_territories.filter(pk=merchant.territory_id).exists():
            return True
        return False
    owned = get_merchant_for_user(user)
    return owned is not None and owned.pk == merchant.pk


def can_manage_merchant_products(user):
    if is_super_admin(user) or is_merchant(user):
        return True
    return user_has_staff_permission(user, 'can_manage_products')


def user_has_staff_permission(user, permission_field):
    from merchants.models import MerchantStaff

    if is_merchant(user):
        return True
    if not is_merchant_staff(user):
        return False
    staff = MerchantStaff.objects.filter(user=user, is_active=True).first()
    return staff and getattr(staff, permission_field, False)


def role_required(*roles):
    """Decorator: restrict view to users with one of the given roles."""

    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped(request, *args, **kwargs):
            role = get_user_role(request.user)
            if is_super_admin(request.user):
                return view_func(request, *args, **kwargs)
            if role in roles:
                return view_func(request, *args, **kwargs)
            raise PermissionDenied
        return _wrapped
    return decorator


def staff_permission_required(permission_field):
    """Decorator for merchant staff with a specific permission flag."""

    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped(request, *args, **kwargs):
            if is_super_admin(request.user) or is_merchant(request.user):
                return view_func(request, *args, **kwargs)
            if user_has_staff_permission(request.user, permission_field):
                return view_func(request, *args, **kwargs)
            raise PermissionDenied
        return _wrapped
    return decorator


def merchant_owner_required(view_func):
    """Ensure user operates on their own merchant; injects merchant into kwargs."""

    @wraps(view_func)
    @login_required
    def _wrapped(request, *args, **kwargs):
        merchant = get_merchant_for_user(request.user)
        if merchant is None and not is_super_admin(request.user):
            messages.error(request, 'No merchant account is linked to your user. Contact support.')
            return redirect('products:home')
        kwargs['merchant'] = merchant
        return view_func(request, *args, **kwargs)
    return _wrapped
