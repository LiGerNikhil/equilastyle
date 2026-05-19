"""
Create or update the Django user account linked to a Merchant (owner login).
"""
from django.db import transaction

from accounts.models import Profile, User


def _split_owner_name(owner_name):
    parts = (owner_name or '').strip().split(None, 1)
    first = parts[0] if parts else 'Merchant'
    last = parts[1] if len(parts) > 1 else ''
    return first, last


def _unique_username(base):
    username = base[:150]
    counter = 1
    while User.objects.filter(username=username).exists():
        suffix = str(counter)
        username = f'{base[:150 - len(suffix)]}{suffix}'
        counter += 1
    return username


@transaction.atomic
def provision_merchant_owner(*, merchant, login_email, password=None, update_password=True):
    """
    Link merchant.owner_user to a User with role=merchant.
    Creates a new user or updates the existing owner / email match.
    """
    login_email = login_email.strip().lower()
    first, last = _split_owner_name(merchant.owner_name)

    user = merchant.owner_user
    if user is None:
        user = User.objects.filter(email__iexact=login_email).first()

    if user is None:
        base = login_email.split('@')[0] or 'merchant'
        user = User(
            username=_unique_username(base),
            email=login_email,
            role=User.Role.MERCHANT,
            phone=merchant.phone or '',
            is_staff=False,
            is_active=True,
        )
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
    else:
        user.email = login_email
        user.role = User.Role.MERCHANT
        user.phone = merchant.phone or user.phone
        user.is_active = True
        if update_password and password:
            user.set_password(password)
        user.save()

    profile, _ = Profile.objects.get_or_create(
        user=user,
        defaults={'first_name': first, 'last_name': last},
    )
    if profile.first_name != first or profile.last_name != last:
        profile.first_name = first
        profile.last_name = last
        profile.save(update_fields=['first_name', 'last_name'])

    if merchant.owner_user_id != user.pk:
        merchant.owner_user = user
        merchant.save(update_fields=['owner_user', 'updated_at'])

    return user
